import { ChatMessage, ChatEntry } from '@/types/os'
import dayjs from 'dayjs'

/**
 * Export chat messages to markdown format
 */
export function exportChatToMarkdown(
  messages: ChatMessage[],
  sessionName?: string
): string {
  const timestamp = dayjs().format('YYYY-MM-DD HH:mm:ss')
  const title = sessionName || 'Chat Export'

  let markdown = `# ${title}\n\n`
  markdown += `*Exported on: ${timestamp}*\n\n`
  markdown += `---\n\n`

  messages.forEach((msg, index) => {
    const role = msg.role === 'agent' ? 'Assistant' : msg.role.charAt(0).toUpperCase() + msg.role.slice(1)
    const time = dayjs(msg.created_at).format('HH:mm:ss')

    markdown += `### ${role} [${time}]\n\n`
    markdown += `${msg.content}\n\n`

    // Add tool calls if present
    if (msg.tool_calls && msg.tool_calls.length > 0) {
      markdown += `#### Tool Calls\n\n`
      msg.tool_calls.forEach((tool) => {
        markdown += `- **${tool.tool_name}**\n`
        markdown += `  \`\`\`json\n`
        markdown += `  ${JSON.stringify(tool.tool_args, null, 2)}\n`
        markdown += `  \`\`\`\n`
        if (tool.content) {
          markdown += `  *Result:* ${tool.content}\n`
        }
        markdown += `\n`
      })
    }

    // Add reasoning steps if present
    if (msg.extra_data?.reasoning_steps && msg.extra_data.reasoning_steps.length > 0) {
      markdown += `#### Reasoning Steps\n\n`
      msg.extra_data.reasoning_steps.forEach((step, i) => {
        markdown += `${i + 1}. **${step.title}**\n`
        markdown += `   - Reasoning: ${step.reasoning}\n`
        markdown += `   - Result: ${step.result}\n\n`
      })
    }

    markdown += `---\n\n`
  })

  return markdown
}

/**
 * Export prompts tailored for different LLM providers
 */
export function exportPromptsForLLM(
  messages: ChatMessage[],
  provider: 'claude' | 'openai' | 'gemini' | 'mistral' = 'claude'
): string {
  const userMessages = messages.filter((m) => m.role === 'user')
  const assistantMessages = messages.filter((m) => m.role === 'agent')

  let output = `# Prompts for ${provider.toUpperCase()}\n\n`
  output += `## Context\n\n`

  // Generate conversation summary
  if (messages.length > 0) {
    output += `This is a conversation exported from Paper2SaaS AgentOS.\n\n`
    output += `Total messages: ${messages.length}\n`
    output += `User messages: ${userMessages.length}\n`
    output += `Assistant responses: ${assistantMessages.length}\n\n`
  }

  output += `## Conversation\n\n`

  // Format based on provider
  messages.forEach((msg) => {
    const role = msg.role === 'agent' ? 'Assistant' : msg.role

    switch (provider) {
      case 'claude':
        if (msg.role === 'user') {
          output += `Human: ${msg.content}\n\n`
        } else if (msg.role === 'agent') {
          output += `Assistant: ${msg.content}\n\n`
        }
        break

      case 'openai':
      case 'mistral':
        output += `**${role}**: ${msg.content}\n\n`
        break

      case 'gemini':
        if (msg.role === 'user') {
          output += `user: ${msg.content}\n\n`
        } else if (msg.role === 'agent') {
          output += `model: ${msg.content}\n\n`
        }
        break
    }
  })

  // Add system prompt suggestion
  output += `\n---\n\n`
  output += `## Suggested System Prompt\n\n`
  output += `You are a helpful AI assistant specialized in analyzing academic papers and generating SaaS business opportunities. `
  output += `Continue the conversation above in the same helpful and analytical tone.\n`

  return output
}

/**
 * Generate a shareable link for the current chat
 */
export function generateShareableLink(
  sessionId: string,
  entityId: string,
  mode: 'agent' | 'team',
  endpoint: string
): string {
  const baseUrl = typeof window !== 'undefined' ? window.location.origin : ''
  const params = new URLSearchParams({
    session: sessionId,
    [mode]: entityId,
    endpoint: endpoint
  })

  return `${baseUrl}?${params.toString()}`
}

/**
 * Copy text to clipboard
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (error) {
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = text
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    document.body.appendChild(textArea)
    textArea.select()
    try {
      document.execCommand('copy')
      document.body.removeChild(textArea)
      return true
    } catch (err) {
      document.body.removeChild(textArea)
      return false
    }
  }
}

/**
 * Download text as a file
 */
export function downloadAsFile(content: string, filename: string): void {
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
