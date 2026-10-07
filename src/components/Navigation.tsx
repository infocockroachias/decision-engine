"use client";

interface NavigationProps {
  currentPage: string;
  onNavigate: (page: string) => void;
}

export default function Navigation({ currentPage, onNavigate }: NavigationProps) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: "📊" },
    { id: "tests", label: "Tests", icon: "📝" },
    { id: "profile", label: "Profile", icon: "👤" },
  ];

  return (
    <nav className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur-sm" role="navigation" aria-label="Main navigation">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <button onClick={() => onNavigate("dashboard")} className="flex items-center gap-2" aria-label="Go to dashboard">
            <div className="h-8 w-8 rounded-lg bg-brand flex items-center justify-center">
              <span className="text-white font-bold text-sm">UPSC</span>
            </div>
            <span className="hidden sm:block font-semibold text-slate-900">Decision Engine</span>
          </button>

          {/* Nav Items */}
          <div className="flex items-center gap-1 sm:gap-2">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-all
                  ${currentPage === item.id ? "bg-brand/10 text-brand" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"}`}
                aria-current={currentPage === item.id ? "page" : undefined}
              >
                <span aria-hidden="true">{item.icon}</span>
                <span className="hidden sm:inline">{item.label}</span>
              </button>
            ))}
          </div>

          {/* User Avatar */}
          <div className="flex items-center gap-2">
            <button className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-200 text-sm" aria-label="User menu">
              👤
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}