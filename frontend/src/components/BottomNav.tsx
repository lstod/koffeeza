import { NavLink } from "react-router-dom";
import { Coffee, Settings } from "lucide-react";
import { cn } from "@/lib/utils";

const links = [
  { to: "/", label: "Log", icon: Coffee },
  { to: "/setup", label: "Setup", icon: Settings },
] as const;

export function BottomNav() {
  return (
    <nav className="fixed inset-x-0 bottom-0 z-50 border-t border-border bg-background">
      <div className="mx-auto flex h-14 max-w-lg items-center justify-around">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              cn(
                "flex flex-col items-center gap-0.5 px-4 py-1.5 text-xs transition-colors",
                isActive
                  ? "text-primary"
                  : "text-muted-foreground hover:text-foreground",
              )
            }
          >
            <Icon className="h-5 w-5" />
            <span>{label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
