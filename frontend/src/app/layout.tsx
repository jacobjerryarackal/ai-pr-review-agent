import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI PR Review Agent",
  description: "Dashboard for AI-powered code reviews",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        <div className="flex h-screen">
          {/* Sidebar */}
          <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
            <div className="p-4 border-b border-gray-200">
              <h1 className="text-xl font-bold text-gray-800">
                AI PR Review
              </h1>
            </div>
            <nav className="flex-1 p-4 space-y-2">
              <NavLink href="/" label="Dashboard" />
              <NavLink href="/queue" label="Approval Queue" />
              <NavLink href="/reviews" label="All Reviews" />
              <NavLink href="/costs" label="Costs" />
              <NavLink href="/settings" label="Settings" />
            </nav>
          </aside>

          {/* Main Content */}
          <main className="flex-1 overflow-auto p-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}

function NavLink({ href, label }: { href: string; label: string }) {
  return (
    <a
      href={href}
      className="block px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition-colors"
    >
      {label}
    </a>
  );
}