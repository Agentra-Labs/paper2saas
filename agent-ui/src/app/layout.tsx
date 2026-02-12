import type { Metadata } from 'next'
import { DM_Mono, Geist } from 'next/font/google'
import { NuqsAdapter } from 'nuqs/adapters/next/app'
import { Toaster } from '@/components/ui/sonner'
import './globals.css'
const geistSans = Geist({
    variable: '--font-geist-sans',
    weight: '400',
    subsets: ['latin']
})

const dmMono = DM_Mono({
    subsets: ['latin'],
    variable: '--font-dm-mono',
    weight: '400'
})

export const metadata: Metadata = {
    title: 'P2S',
    description:
        'Multi-agent system for analyzing arXiv papers and generating SaaS ideas',
    icons: {
        icon: '/icon.svg'
    }
}

export default function RootLayout({
    children
}: Readonly<{
    children: React.ReactNode
}>) {
    return (
        <html lang="en" suppressHydrationWarning>
            <body className={`${geistSans.variable} ${dmMono.variable} antialiased`} suppressHydrationWarning>
                <NuqsAdapter>{children}</NuqsAdapter>
                <Toaster />
            </body>
        </html>
    )
}
