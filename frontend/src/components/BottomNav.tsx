import { useState } from "react";
import { NavLink } from "react-router-dom";
import { ClipboardList, Coffee, Settings, UserCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

const links = [
  { to: "/", label: "Log", icon: Coffee },
  { to: "/history", label: "History", icon: ClipboardList },
  { to: "/setup", label: "Setup", icon: Settings },
] as const;

export function BottomNav() {
  const { user, logout } = useAuth();
  const [showSwitch, setShowSwitch] = useState(false);

  return (
    <>
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

          <button
            onClick={() => setShowSwitch(true)}
            className="flex flex-col items-center gap-0.5 px-4 py-1.5 text-xs text-muted-foreground transition-colors hover:text-foreground"
          >
            <UserCircle className="h-5 w-5" />
            <span className="max-w-[4rem] truncate">{user?.name}</span>
          </button>
        </div>
      </nav>

      <Dialog open={showSwitch} onOpenChange={setShowSwitch}>
        <DialogContent className="max-w-xs">
          <DialogHeader>
            <DialogTitle>Switch user?</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            You&apos;re signed in as <strong>{user?.name}</strong>. Switching
            will return you to the profile picker.
          </p>
          <div className="flex gap-3 pt-2">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => setShowSwitch(false)}
            >
              Cancel
            </Button>
            <Button className="flex-1" onClick={logout}>
              Switch
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
