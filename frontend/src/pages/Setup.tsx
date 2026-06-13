import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  createBean,
  createGrinder,
  createMachine,
  fetchBeans,
  fetchGrinders,
  fetchMachines,
} from "@/lib/api";
import type {
  BeanResponse,
  GrinderResponse,
  MachineResponse,
  ScaleType,
} from "@/lib/types";
import { SCALE_TYPE_OPTIONS } from "@/lib/types";

// ── Beans Tab ──────────────────────────────────────────────────────────────

function BeansTab() {
  const [beans, setBeans] = useState<BeanResponse[]>([]);
  const [loadKey, setLoadKey] = useState(0);
  const [open, setOpen] = useState(false);
  const [brand, setBrand] = useState("");
  const [product, setProduct] = useState("");
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchBeans().then((data) => {
      if (!cancelled) setBeans(data);
    });
    return () => {
      cancelled = true;
    };
  }, [loadKey]);

  async function handleSave() {
    if (!brand.trim() || !product.trim()) return;
    setSaving(true);
    try {
      await createBean({
        brand: brand.trim(),
        product: product.trim(),
        notes: notes.trim() || null,
      });
      setBrand("");
      setProduct("");
      setNotes("");
      setOpen(false);
      setLoadKey((k) => k + 1);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-medium">Beans</h2>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm">
              <Plus className="mr-1 h-4 w-4" /> Add Bean
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Bean</DialogTitle>
              <DialogDescription>
                Add a new coffee bean to your collection.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Brand</Label>
                <Input
                  value={brand}
                  onChange={(e) => setBrand(e.target.value)}
                  placeholder="e.g. Onyx"
                />
              </div>
              <div className="space-y-2">
                <Label>Product</Label>
                <Input
                  value={product}
                  onChange={(e) => setProduct(e.target.value)}
                  placeholder="e.g. Tropical Weather"
                />
              </div>
              <div className="space-y-2">
                <Label>
                  Notes{" "}
                  <span className="text-muted-foreground">(optional)</span>
                </Label>
                <Input
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g. Light roast, fruity"
                />
              </div>
              <Button
                onClick={handleSave}
                disabled={saving || !brand.trim() || !product.trim()}
                className="w-full"
              >
                {saving ? "Saving…" : "Save"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {beans.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          No beans added yet. Tap &ldquo;Add Bean&rdquo; to get started.
        </p>
      ) : (
        <div className="space-y-2">
          {beans.map((b) => (
            <Card key={b.id}>
              <CardHeader className="p-4">
                <CardTitle className="text-base">
                  {b.brand} — {b.product}
                </CardTitle>
                {b.notes && (
                  <CardDescription className="text-xs">
                    {b.notes}
                  </CardDescription>
                )}
              </CardHeader>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Grinders Tab ───────────────────────────────────────────────────────────

function GrindersTab() {
  const [grinders, setGrinders] = useState<GrinderResponse[]>([]);
  const [loadKey, setLoadKey] = useState(0);
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const [brand, setBrand] = useState("");
  const [model, setModel] = useState("");
  const [label, setLabel] = useState("");
  const [scaleType, setScaleType] = useState<ScaleType>("STEPPED");
  const [stepNative, setStepNative] = useState("1");
  const [finerIsLower, setFinerIsLower] = useState(true);
  const [snap, setSnap] = useState("1");
  const [minNative, setMinNative] = useState("");
  const [maxNative, setMaxNative] = useState("");
  const [unitLabel, setUnitLabel] = useState("");

  useEffect(() => {
    let cancelled = false;
    fetchGrinders().then((data) => {
      if (!cancelled) setGrinders(data);
    });
    return () => {
      cancelled = true;
    };
  }, [loadKey]);

  function resetForm() {
    setBrand("");
    setModel("");
    setLabel("");
    setScaleType("STEPPED");
    setStepNative("1");
    setFinerIsLower(true);
    setSnap("1");
    setMinNative("");
    setMaxNative("");
    setUnitLabel("");
  }

  async function handleSave() {
    if (!brand.trim() || !model.trim()) return;
    setSaving(true);
    try {
      await createGrinder({
        brand: brand.trim(),
        model: model.trim(),
        label: label.trim() || null,
        scale_type: scaleType,
        step_native: Number(stepNative),
        finer_is_lower: finerIsLower,
        snap: Number(snap),
        min_native: minNative ? Number(minNative) : null,
        max_native: maxNative ? Number(maxNative) : null,
        unit_label: unitLabel,
      });
      resetForm();
      setOpen(false);
      setLoadKey((k) => k + 1);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-medium">Grinders</h2>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm">
              <Plus className="mr-1 h-4 w-4" /> Add Grinder
            </Button>
          </DialogTrigger>
          <DialogContent className="max-h-[85svh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Add Grinder</DialogTitle>
              <DialogDescription>
                Configure your grinder and its adapter profile.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Brand</Label>
                <Input
                  value={brand}
                  onChange={(e) => setBrand(e.target.value)}
                  placeholder="e.g. Niche"
                />
              </div>
              <div className="space-y-2">
                <Label>Model</Label>
                <Input
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  placeholder="e.g. Zero"
                />
              </div>
              <div className="space-y-2">
                <Label>
                  Label{" "}
                  <span className="text-muted-foreground">(optional)</span>
                </Label>
                <Input
                  value={label}
                  onChange={(e) => setLabel(e.target.value)}
                  placeholder="e.g. Kitchen grinder"
                />
              </div>
              <div className="space-y-2">
                <Label>Scale Type</Label>
                <Select
                  value={scaleType}
                  onValueChange={(v) => setScaleType(v as ScaleType)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {SCALE_TYPE_OPTIONS.map((s) => (
                      <SelectItem key={s} value={s}>
                        {s}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  Stepped = numbered dial, Clicks = relative clicks, Stepless =
                  continuous dial
                </p>
              </div>
              <div className="space-y-2">
                <Label>Step Size (native units per standard step)</Label>
                <Input
                  type="number"
                  step="0.1"
                  min="0.1"
                  value={stepNative}
                  onChange={(e) => setStepNative(e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  How many of the grinder&apos;s own units equal one standard
                  grind adjustment
                </p>
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Finer = Lower Number</Label>
                  <p className="text-xs text-muted-foreground">
                    Most grinders: finer grind = lower setting number
                  </p>
                </div>
                <Switch
                  checked={finerIsLower}
                  onCheckedChange={setFinerIsLower}
                />
              </div>
              <div className="space-y-2">
                <Label>Snap (smallest achievable step)</Label>
                <Input
                  type="number"
                  step="0.5"
                  min="0.5"
                  value={snap}
                  onChange={(e) => setSnap(e.target.value)}
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label>
                    Min{" "}
                    <span className="text-muted-foreground">(optional)</span>
                  </Label>
                  <Input
                    type="number"
                    value={minNative}
                    onChange={(e) => setMinNative(e.target.value)}
                    placeholder="e.g. 1"
                  />
                </div>
                <div className="space-y-2">
                  <Label>
                    Max{" "}
                    <span className="text-muted-foreground">(optional)</span>
                  </Label>
                  <Input
                    type="number"
                    value={maxNative}
                    onChange={(e) => setMaxNative(e.target.value)}
                    placeholder="e.g. 40"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Unit Label</Label>
                <Input
                  value={unitLabel}
                  onChange={(e) => setUnitLabel(e.target.value)}
                  placeholder='e.g. clicks, °, or leave empty'
                />
              </div>
              <Button
                onClick={handleSave}
                disabled={saving || !brand.trim() || !model.trim()}
                className="w-full"
              >
                {saving ? "Saving…" : "Save"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {grinders.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          No grinders added yet. Tap &ldquo;Add Grinder&rdquo; to get started.
        </p>
      ) : (
        <div className="space-y-2">
          {grinders.map((g) => (
            <Card key={g.id}>
              <CardHeader className="p-4">
                <CardTitle className="text-base">
                  {g.brand} {g.model}
                  {g.label ? ` (${g.label})` : ""}
                </CardTitle>
                <CardDescription className="text-xs">
                  {g.scale_type} · step {g.step_native}
                  {g.unit_label ? ` ${g.unit_label}` : ""} · snap {g.snap}
                </CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Machines Tab ───────────────────────────────────────────────────────────

function MachinesTab() {
  const [machines, setMachines] = useState<MachineResponse[]>([]);
  const [loadKey, setLoadKey] = useState(0);
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const [brand, setBrand] = useState("");
  const [model, setModel] = useState("");
  const [label, setLabel] = useState("");
  const [notes, setNotes] = useState("");

  useEffect(() => {
    let cancelled = false;
    fetchMachines().then((data) => {
      if (!cancelled) setMachines(data);
    });
    return () => {
      cancelled = true;
    };
  }, [loadKey]);

  async function handleSave() {
    if (!brand.trim() || !model.trim()) return;
    setSaving(true);
    try {
      await createMachine({
        brand: brand.trim(),
        model: model.trim(),
        label: label.trim() || null,
        notes: notes.trim() || null,
      });
      setBrand("");
      setModel("");
      setLabel("");
      setNotes("");
      setOpen(false);
      setLoadKey((k) => k + 1);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-medium">Machines</h2>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm">
              <Plus className="mr-1 h-4 w-4" /> Add Machine
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Machine</DialogTitle>
              <DialogDescription>
                Add a new espresso machine.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Brand</Label>
                <Input
                  value={brand}
                  onChange={(e) => setBrand(e.target.value)}
                  placeholder="e.g. Breville"
                />
              </div>
              <div className="space-y-2">
                <Label>Model</Label>
                <Input
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  placeholder="e.g. Bambino Plus"
                />
              </div>
              <div className="space-y-2">
                <Label>
                  Label{" "}
                  <span className="text-muted-foreground">(optional)</span>
                </Label>
                <Input
                  value={label}
                  onChange={(e) => setLabel(e.target.value)}
                  placeholder="e.g. Home machine"
                />
              </div>
              <div className="space-y-2">
                <Label>
                  Notes{" "}
                  <span className="text-muted-foreground">(optional)</span>
                </Label>
                <Input
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g. 9 bar, 58mm basket"
                />
              </div>
              <Button
                onClick={handleSave}
                disabled={saving || !brand.trim() || !model.trim()}
                className="w-full"
              >
                {saving ? "Saving…" : "Save"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {machines.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          No machines added yet. Tap &ldquo;Add Machine&rdquo; to get started.
        </p>
      ) : (
        <div className="space-y-2">
          {machines.map((m) => (
            <Card key={m.id}>
              <CardHeader className="p-4">
                <CardTitle className="text-base">
                  {m.brand} {m.model}
                  {m.label ? ` (${m.label})` : ""}
                </CardTitle>
                {m.notes && (
                  <CardDescription className="text-xs">
                    {m.notes}
                  </CardDescription>
                )}
              </CardHeader>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Setup Page ─────────────────────────────────────────────────────────────

export function Setup() {
  return (
    <div className="p-4">
      <h1 className="mb-4 text-xl font-semibold tracking-tight">Setup</h1>
      <Tabs defaultValue="beans">
        <TabsList className="w-full">
          <TabsTrigger value="beans" className="flex-1">
            Beans
          </TabsTrigger>
          <TabsTrigger value="grinders" className="flex-1">
            Grinders
          </TabsTrigger>
          <TabsTrigger value="machines" className="flex-1">
            Machines
          </TabsTrigger>
        </TabsList>
        <TabsContent value="beans">
          <BeansTab />
        </TabsContent>
        <TabsContent value="grinders">
          <GrindersTab />
        </TabsContent>
        <TabsContent value="machines">
          <MachinesTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
