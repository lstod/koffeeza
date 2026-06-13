import { useEffect, useState } from "react";
import { Loader2, Plus, Lock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";
import { fetchUsers, createUser, loginUser } from "@/lib/api";
import type { UserResponse } from "@/lib/types";
import { useAuth } from "@/contexts/AuthContext";

function getInitials(name: string): string {
  return name
    .split(/\s+/)
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

const AVATAR_COLORS = [
  "bg-blue-600",
  "bg-emerald-600",
  "bg-amber-600",
  "bg-rose-600",
  "bg-violet-600",
  "bg-cyan-600",
  "bg-pink-600",
  "bg-teal-600",
];

export function UserPicker() {
  const { login } = useAuth();
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const [pinUser, setPinUser] = useState<UserResponse | null>(null);
  const [pin, setPin] = useState("");
  const [pinError, setPinError] = useState("");
  const [pinLoading, setPinLoading] = useState(false);

  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newPin, setNewPin] = useState("");
  const [createError, setCreateError] = useState("");
  const [createLoading, setCreateLoading] = useState(false);

  useEffect(() => {
    fetchUsers()
      .then(setUsers)
      .finally(() => setLoading(false));
  }, []);

  async function handleSelectUser(user: UserResponse) {
    if (user.has_pin) {
      setPinUser(user);
      setPin("");
      setPinError("");
      return;
    }

    try {
      const res = await loginUser(user.id);
      login(res.user, res.token);
    } catch (err) {
      setPinError(err instanceof Error ? err.message : "Login failed");
    }
  }

  async function handlePinSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!pinUser) return;
    setPinLoading(true);
    setPinError("");
    try {
      const res = await loginUser(pinUser.id, pin);
      login(res.user, res.token);
    } catch {
      setPinError("Incorrect PIN");
    } finally {
      setPinLoading(false);
    }
  }

  async function handleCreateSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!newName.trim()) return;
    setCreateLoading(true);
    setCreateError("");
    try {
      const res = await createUser(newName.trim(), newPin || undefined);
      login(res.user, res.token);
    } catch (err) {
      setCreateError(
        err instanceof Error ? err.message : "Failed to create profile",
      );
    } finally {
      setCreateLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-svh items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="mx-auto flex min-h-svh max-w-lg flex-col items-center justify-center gap-8 p-6">
      <div className="text-center">
        <h1 className="text-2xl font-semibold tracking-tight">Koffeeza</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          {users.length > 0 ? "Who's making coffee?" : "Create your profile to get started"}
        </p>
      </div>

      {users.length > 0 && (
        <div className="grid w-full grid-cols-2 gap-3 sm:grid-cols-3">
          {users.map((user, i) => (
            <button
              key={user.id}
              onClick={() => handleSelectUser(user)}
              className={cn(
                "flex flex-col items-center gap-2 rounded-xl border border-border p-4",
                "transition-colors hover:bg-secondary/50 active:bg-secondary",
              )}
            >
              <div
                className={cn(
                  "flex h-14 w-14 items-center justify-center rounded-full text-lg font-semibold text-white",
                  AVATAR_COLORS[i % AVATAR_COLORS.length],
                )}
              >
                {getInitials(user.name)}
              </div>
              <span className="flex items-center gap-1 text-sm font-medium">
                {user.name}
                {user.has_pin && (
                  <Lock className="h-3 w-3 text-muted-foreground" />
                )}
              </span>
            </button>
          ))}
        </div>
      )}

      <Button
        variant="outline"
        className="h-12 w-full max-w-xs gap-2"
        onClick={() => {
          setShowCreate(true);
          setNewName("");
          setNewPin("");
          setCreateError("");
        }}
      >
        <Plus className="h-4 w-4" />
        Create Profile
      </Button>

      {/* PIN dialog */}
      <Dialog
        open={!!pinUser}
        onOpenChange={(open) => !open && setPinUser(null)}
      >
        <DialogContent className="max-w-xs">
          <DialogHeader>
            <DialogTitle>Enter PIN for {pinUser?.name}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handlePinSubmit} className="space-y-4">
            <Input
              type="password"
              inputMode="numeric"
              maxLength={6}
              placeholder="PIN"
              value={pin}
              onChange={(e) => setPin(e.target.value)}
              autoFocus
            />
            {pinError && (
              <p className="text-sm text-destructive-foreground">{pinError}</p>
            )}
            <Button
              type="submit"
              className="h-10 w-full"
              disabled={pinLoading || !pin}
            >
              {pinLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                "Unlock"
              )}
            </Button>
          </form>
        </DialogContent>
      </Dialog>

      {/* Create profile dialog */}
      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent className="max-w-xs">
          <DialogHeader>
            <DialogTitle>New Profile</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreateSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="new-name">Name</Label>
              <Input
                id="new-name"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Your name"
                autoFocus
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-pin">
                PIN <span className="text-muted-foreground">(optional)</span>
              </Label>
              <Input
                id="new-pin"
                type="password"
                inputMode="numeric"
                maxLength={6}
                value={newPin}
                onChange={(e) => setNewPin(e.target.value)}
                placeholder="4-6 digits"
              />
            </div>
            {createError && (
              <p className="text-sm text-destructive-foreground">
                {createError}
              </p>
            )}
            <Button
              type="submit"
              className="h-10 w-full"
              disabled={createLoading || !newName.trim()}
            >
              {createLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                "Create"
              )}
            </Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
