'use client'

import { useState } from 'react'
import { Button } from '../../../ui/button'
import Icon from '@/components/ui/icon'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger
} from '../../../ui/dropdown-menu'
import { toast } from 'sonner'
import {
  exportChatToMarkdown,
  exportPromptsForLLM,
  generateShareableLink,
  copyToClipboard,
  downloadAsFile
} from '@/lib/exportUtils'
import { useStore } from '@/store'
import { useQueryState } from 'nuqs'

interface ExportMenuProps {
  sessionId: string
  sessionName: string
}

const ExportMenu = ({ sessionId, sessionName }: ExportMenuProps) => {
  const { messages, selectedEndpoint, mode } = useStore()
  const [agentId] = useQueryState('agent')
  const [teamId] = useQueryState('team')
  const [isOpen, setIsOpen] = useState(false)

  const entityId = mode === 'agent' ? agentId : teamId

  const handleExportMarkdown = () => {
    if (messages.length === 0) {
      toast.error('No messages to export')
      return
    }

    const markdown = exportChatToMarkdown(messages, sessionName)
    const filename = `${sessionName.replace(/[^a-z0-9]/gi, '_')}_${new Date().getTime()}.md`
    downloadAsFile(markdown, filename)
    toast.success('Chat exported as Markdown')
    setIsOpen(false)
  }

  const handleExportPrompts = (provider: 'claude' | 'openai' | 'gemini' | 'mistral') => {
    if (messages.length === 0) {
      toast.error('No messages to export')
      return
    }

    const prompts = exportPromptsForLLM(messages, provider)
    const filename = `prompts_${provider}_${new Date().getTime()}.md`
    downloadAsFile(prompts, filename)
    toast.success(`Prompts exported for ${provider.toUpperCase()}`)
    setIsOpen(false)
  }

  const handleCopyShareLink = async () => {
    if (!entityId) {
      toast.error('No agent or team selected')
      return
    }

    const shareLink = generateShareableLink(
      sessionId,
      entityId,
      mode,
      selectedEndpoint
    )
    const success = await copyToClipboard(shareLink)

    if (success) {
      toast.success('Share link copied to clipboard')
    } else {
      toast.error('Failed to copy link')
    }
    setIsOpen(false)
  }

  const handleCopyMessages = async () => {
    if (messages.length === 0) {
      toast.error('No messages to copy')
      return
    }

    const markdown = exportChatToMarkdown(messages, sessionName)
    const success = await copyToClipboard(markdown)

    if (success) {
      toast.success('Messages copied to clipboard')
    } else {
      toast.error('Failed to copy messages')
    }
    setIsOpen(false)
  }

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="transform opacity-0 transition-all duration-200 ease-in-out group-hover:opacity-100"
          onClick={(e) => e.stopPropagation()}
        >
          <Icon type="share" size="xs" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuItem onClick={handleCopyShareLink}>
          <Icon type="link" size="xs" className="mr-2" />
          Copy share link
        </DropdownMenuItem>
        <DropdownMenuItem onClick={handleCopyMessages}>
          <Icon type="clipboard" size="xs" className="mr-2" />
          Copy to clipboard
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleExportMarkdown}>
          <Icon type="download" size="xs" className="mr-2" />
          Export as Markdown
        </DropdownMenuItem>
        <DropdownMenuSub>
          <DropdownMenuSubTrigger>
            <Icon type="sparkles" size="xs" className="mr-2" />
            Export for LLM
          </DropdownMenuSubTrigger>
          <DropdownMenuSubContent>
            <DropdownMenuItem onClick={() => handleExportPrompts('claude')}>
              Claude (Anthropic)
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleExportPrompts('openai')}>
              ChatGPT (OpenAI)
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleExportPrompts('gemini')}>
              Gemini (Google)
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleExportPrompts('mistral')}>
              Mistral AI
            </DropdownMenuItem>
          </DropdownMenuSubContent>
        </DropdownMenuSub>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export default ExportMenu
