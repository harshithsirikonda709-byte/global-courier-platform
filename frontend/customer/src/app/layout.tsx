import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'GLOBAL COURIER | Send Love From India Worldwide',
  description:
    'Doorstep international courier platform helping Indian families send clothes, permitted homemade food products, gifts, and personal belongings to loved ones abroad.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-white text-[#0B1F3A] font-sans">
        {children}
      </body>
    </html>
  );
}
