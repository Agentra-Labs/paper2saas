'use client'

import * as React from 'react'
import {
    Select,
    SelectTrigger,
    SelectValue,
    SelectContent,
    SelectItem
} from '@/components/ui/select'
import { useStore } from '@/store'

export function ModeSelector() {
    const mode = useStore((state) => state.mode)
    const setMode = useStore((state) => state.setMode)
    const setMessages = useStore((state) => state.setMessages)
    const setSelectedModel = useStore((state) => state.setSelectedModel)
    const hydrated = useStore((state) => state.hydrated)

    // Use a ref to track current mode to avoid infinite loop
    const modeRef = React.useRef(mode)
    React.useEffect(() => {
        modeRef.current = mode
    }, [mode])

    const handleModeChange = React.useCallback((newMode: string) => {
        if (newMode === modeRef.current) return
        setMode(newMode as 'agent' | 'team')
        setSelectedModel('')
        setMessages([])
    }, [setMode, setSelectedModel, setMessages])

    // Don't render until hydrated to avoid SSR/client mismatch
    if (!hydrated) {
        return (
            <div className="h-9 w-full rounded-xl border border-primary/15 bg-primaryAccent text-xs font-medium uppercase animate-pulse" />
        )
    }

    return (
        <Select
            value={mode}
            onValueChange={handleModeChange}
        >
            <SelectTrigger className="h-9 w-full rounded-xl border border-primary/15 bg-primaryAccent text-xs font-medium uppercase">
                <SelectValue />
            </SelectTrigger>
            <SelectContent className="border-none bg-primaryAccent font-dmmono shadow-lg">
                <SelectItem value="agent" className="cursor-pointer">
                    <div className="text-xs font-medium uppercase">Agent</div>
                </SelectItem>

                <SelectItem value="team" className="cursor-pointer">
                    <div className="text-xs font-medium uppercase">Team</div>
                </SelectItem>
            </SelectContent>
        </Select>
    )
}
