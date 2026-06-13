import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import {
  fetchBeans,
  fetchGrinders,
  fetchMachines,
  fetchPreferences,
  fetchRecall,
  createShot,
} from "@/lib/api";
import type {
  BeanResponse,
  GrinderResponse,
  Intensity,
  MachineResponse,
  RecallResponse,
  Taste,
} from "@/lib/types";
import { TASTE_OPTIONS, INTENSITY_OPTIONS } from "@/lib/types";
import { useAuth } from "@/contexts/AuthContext";

function userKey(userId: number, key: string) {
  return `koffeeza_user_${userId}_${key}`;
}

const TASTE_LABELS: Record<Taste, string> = {
  SOUR: "Sour",
  BITTER: "Bitter",
  BALANCED: "Balanced",
  WEAK: "Weak",
  ASTRINGENT: "Astringent",
};

const CONFIDENCE_VARIANT: Record<string, "default" | "secondary" | "outline"> =
  {
    EXACT: "default",
    APPROXIMATE: "secondary",
    GENERIC: "outline",
  };

export function LogShot() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const GRINDER_KEY = userKey(user!.id, "grinder_id");
  const MACHINE_KEY = userKey(user!.id, "machine_id");

  const [beans, setBeans] = useState<BeanResponse[]>([]);
  const [grinders, setGrinders] = useState<GrinderResponse[]>([]);
  const [machines, setMachines] = useState<MachineResponse[]>([]);

  const [beanId, setBeanId] = useState<string>("");
  const [grinderId, setGrinderId] = useState<string>("");
  const [machineId, setMachineId] = useState<string>("");

  const [dose, setDose] = useState("");
  const [yieldG, setYieldG] = useState("");
  const [time, setTime] = useState("");
  const [grindSetting, setGrindSetting] = useState("");
  const [taste, setTaste] = useState<Taste | null>(null);
  const [intensity, setIntensity] = useState<Intensity | null>(null);
  const [roastDate, setRoastDate] = useState("");

  const [recall, setRecall] = useState<RecallResponse | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    async function load() {
      const [b, g, m] = await Promise.all([
        fetchBeans(),
        fetchGrinders(),
        fetchMachines(),
      ]);
      setBeans(b);
      setGrinders(g);
      setMachines(m);
      setLoaded(true);

      try {
        const prefs = await fetchPreferences();
        const savedGrinder =
          prefs.grinder_id?.toString() ??
          localStorage.getItem(GRINDER_KEY) ??
          "";
        const savedMachine =
          prefs.machine_id?.toString() ??
          localStorage.getItem(MACHINE_KEY) ??
          "";
        if (savedGrinder && g.some((x) => x.id.toString() === savedGrinder))
          setGrinderId(savedGrinder);
        if (savedMachine && m.some((x) => x.id.toString() === savedMachine))
          setMachineId(savedMachine);
      } catch {
        const savedGrinder =
          localStorage.getItem(GRINDER_KEY) ?? "";
        const savedMachine =
          localStorage.getItem(MACHINE_KEY) ?? "";
        if (savedGrinder && g.some((x) => x.id.toString() === savedGrinder))
          setGrinderId(savedGrinder);
        if (savedMachine && m.some((x) => x.id.toString() === savedMachine))
          setMachineId(savedMachine);
      }
    }
    load();
  }, [GRINDER_KEY, MACHINE_KEY]);

  const triggerRecall = useCallback(
    async (bean: string, grinder: string, machine: string) => {
      if (!bean || !grinder || !machine) return;
      try {
        const result = await fetchRecall(
          Number(bean),
          Number(grinder),
          Number(machine),
        );
        setRecall(result);
        setDose(result.dose_g.toString());
        setYieldG(result.yield_g.toString());
        setTime(result.time_s.toString());
        if (result.grind_setting_native) {
          setGrindSetting(result.grind_setting_native);
        }
      } catch {
        setRecall(null);
      }
    },
    [],
  );

  function handleBeanChange(value: string) {
    setBeanId(value);
    triggerRecall(value, grinderId, machineId);
  }

  function handleGrinderChange(value: string) {
    setGrinderId(value);
    localStorage.setItem(GRINDER_KEY, value);
    triggerRecall(beanId, value, machineId);
  }

  function handleMachineChange(value: string) {
    setMachineId(value);
    localStorage.setItem(MACHINE_KEY, value);
    triggerRecall(beanId, grinderId, value);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!beanId || !grinderId || !machineId) {
      setError("Please select a bean, grinder, and machine.");
      return;
    }
    if (!dose || !yieldG || !time || !grindSetting) {
      setError("Please fill in dose, yield, time, and grind setting.");
      return;
    }

    setSubmitting(true);
    try {
      const suggestion = await createShot({
        bean_id: Number(beanId),
        grinder_id: Number(grinderId),
        machine_id: Number(machineId),
        grind_setting_native: grindSetting,
        dose_g: Number(dose),
        yield_g: Number(yieldG),
        time_s: Number(time),
        taste,
        intensity,
        roast_date: roastDate || null,
      });
      navigate("/suggestion", { state: { suggestion } });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to log shot");
    } finally {
      setSubmitting(false);
    }
  }

  const needsSetup =
    loaded && (!beans.length || !grinders.length || !machines.length);

  if (!loaded) {
    return (
      <div className="flex min-h-[60svh] items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (needsSetup) {
    return (
      <div className="flex min-h-[60svh] flex-col items-center justify-center gap-6 p-6 text-center">
        <h1 className="text-xl font-semibold tracking-tight">
          Welcome to Koffeeza
        </h1>
        <p className="max-w-xs text-sm text-muted-foreground">
          Before you can log a shot, set up your equipment.
        </p>
        <ul className="space-y-3 text-left text-sm">
          <li className="flex items-center gap-2">
            {beans.length ? (
              <CheckCircle2 className="h-5 w-5 text-primary" />
            ) : (
              <Circle className="h-5 w-5 text-muted-foreground" />
            )}
            <span className={beans.length ? "text-muted-foreground" : ""}>
              Add a bean
            </span>
          </li>
          <li className="flex items-center gap-2">
            {grinders.length ? (
              <CheckCircle2 className="h-5 w-5 text-primary" />
            ) : (
              <Circle className="h-5 w-5 text-muted-foreground" />
            )}
            <span className={grinders.length ? "text-muted-foreground" : ""}>
              Add a grinder
            </span>
          </li>
          <li className="flex items-center gap-2">
            {machines.length ? (
              <CheckCircle2 className="h-5 w-5 text-primary" />
            ) : (
              <Circle className="h-5 w-5 text-muted-foreground" />
            )}
            <span className={machines.length ? "text-muted-foreground" : ""}>
              Add a machine
            </span>
          </li>
        </ul>
        <Button asChild className="h-12 w-full max-w-xs text-base">
          <Link to="/setup">Go to Setup</Link>
        </Button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5 p-4">
      <h1 className="text-xl font-semibold tracking-tight">Log a Shot</h1>

      {recall && (
        <div className="flex items-center gap-2">
          <Badge variant={CONFIDENCE_VARIANT[recall.confidence_label]}>
            {recall.confidence_label}
          </Badge>
          <span className="text-sm text-muted-foreground">
            {recall.confidence_label === "GENERIC"
              ? "Using default starting point"
              : "Pre-filled from previous shot"}
          </span>
        </div>
      )}

      {/* Bean selector */}
      <div className="space-y-2">
        <Label htmlFor="bean">Bean</Label>
        <Select value={beanId} onValueChange={handleBeanChange}>
          <SelectTrigger id="bean">
            <SelectValue placeholder="Select a bean" />
          </SelectTrigger>
          <SelectContent>
            {beans.map((b) => (
              <SelectItem key={b.id} value={b.id.toString()}>
                {b.brand} — {b.product}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Grinder + Machine row */}
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-2">
          <Label htmlFor="grinder">Grinder</Label>
          <Select value={grinderId} onValueChange={handleGrinderChange}>
            <SelectTrigger id="grinder">
              <SelectValue placeholder="Grinder" />
            </SelectTrigger>
            <SelectContent>
              {grinders.map((g) => (
                <SelectItem key={g.id} value={g.id.toString()}>
                  {g.label ?? `${g.brand} ${g.model}`}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="machine">Machine</Label>
          <Select value={machineId} onValueChange={handleMachineChange}>
            <SelectTrigger id="machine">
              <SelectValue placeholder="Machine" />
            </SelectTrigger>
            <SelectContent>
              {machines.map((m) => (
                <SelectItem key={m.id} value={m.id.toString()}>
                  {m.label ?? `${m.brand} ${m.model}`}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Numeric inputs */}
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-2">
          <Label htmlFor="dose">Dose (g)</Label>
          <Input
            id="dose"
            type="number"
            step="0.1"
            min="0"
            value={dose}
            onChange={(e) => setDose(e.target.value)}
            placeholder="18.0"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="yield">Yield (g)</Label>
          <Input
            id="yield"
            type="number"
            step="0.1"
            min="0"
            value={yieldG}
            onChange={(e) => setYieldG(e.target.value)}
            placeholder="36.0"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="time">Time (s)</Label>
          <Input
            id="time"
            type="number"
            step="1"
            min="0"
            value={time}
            onChange={(e) => setTime(e.target.value)}
            placeholder="28"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="grind">Grind Setting</Label>
          <Input
            id="grind"
            type="text"
            value={grindSetting}
            onChange={(e) => setGrindSetting(e.target.value)}
            placeholder="12"
          />
        </div>
      </div>

      {/* Taste buttons */}
      <div className="space-y-2">
        <Label>
          Taste <span className="text-muted-foreground">(optional)</span>
        </Label>
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-5">
          {TASTE_OPTIONS.map((t) => (
            <Button
              key={t}
              type="button"
              variant={taste === t ? "default" : "secondary"}
              className={cn("h-12 text-sm", taste === t && "ring-2 ring-ring")}
              onClick={() => {
                setTaste(t);
                if (t === "BALANCED") setIntensity(null);
              }}
            >
              {TASTE_LABELS[t]}
            </Button>
          ))}
        </div>
      </div>

      {/* Intensity (only if non-balanced taste) */}
      {taste && taste !== "BALANCED" && (
        <div className="space-y-2">
          <Label>Intensity</Label>
          <div className="flex gap-2">
            {INTENSITY_OPTIONS.map((i) => (
              <Button
                key={i}
                type="button"
                variant={intensity === i ? "default" : "secondary"}
                className={cn(
                  "h-10 flex-1",
                  intensity === i && "ring-2 ring-ring",
                )}
                onClick={() => setIntensity(intensity === i ? null : i)}
              >
                {i === "MILD" ? "Mild" : "Strong"}
              </Button>
            ))}
          </div>
        </div>
      )}

      {/* Roast date */}
      <div className="space-y-2">
        <Label htmlFor="roast-date">
          Roast Date <span className="text-muted-foreground">(optional)</span>
        </Label>
        <Input
          id="roast-date"
          type="date"
          value={roastDate}
          onChange={(e) => setRoastDate(e.target.value)}
        />
      </div>

      {error && (
        <p className="text-sm text-destructive-foreground">{error}</p>
      )}

      <Button
        type="submit"
        className="h-12 w-full text-base"
        disabled={submitting}
      >
        {submitting ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Logging…
          </>
        ) : (
          "Log Shot"
        )}
      </Button>
    </form>
  );
}
