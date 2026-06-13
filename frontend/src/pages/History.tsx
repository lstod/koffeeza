import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { fetchShots, fetchBeans } from "@/lib/api";
import type { ShotResponse, BeanResponse } from "@/lib/types";

const REASON_LABELS: Record<string, string> = {
  DIALED_IN: "Dialed in",
  FLOW_TOO_FAST: "Way too fast",
  FLOW_TOO_SLOW: "Way too slow",
  FLOW_FAST: "Running fast",
  FLOW_SLOW: "Running slow",
  TASTE_SOUR: "Sour",
  TASTE_BITTER: "Bitter",
  TASTE_WEAK: "Weak",
  TASTE_ASTRINGENT: "Astringent",
  CHANNELING_SUSPECTED: "Channeling?",
};

const REASON_VARIANT: Record<string, "default" | "secondary" | "outline"> = {
  DIALED_IN: "default",
  CHANNELING_SUSPECTED: "outline",
};

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function History() {
  const [shots, setShots] = useState<ShotResponse[]>([]);
  const [beans, setBeans] = useState<BeanResponse[]>([]);
  const [beanFilter, setBeanFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchShots(), fetchBeans()]).then(([s, b]) => {
      setShots(s);
      setBeans(b);
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    if (beanFilter === "all") {
      fetchShots().then(setShots);
    } else {
      fetchShots(Number(beanFilter)).then(setShots);
    }
  }, [beanFilter]);

  const beanMap = new Map(beans.map((b) => [b.id, b]));

  if (loading) {
    return (
      <div className="flex min-h-[60svh] items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4">
      <h1 className="text-xl font-semibold tracking-tight">Shot History</h1>

      {beans.length > 1 && (
        <div className="space-y-2">
          <Label htmlFor="bean-filter">Filter by bean</Label>
          <Select value={beanFilter} onValueChange={setBeanFilter}>
            <SelectTrigger id="bean-filter">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All beans</SelectItem>
              {beans.map((b) => (
                <SelectItem key={b.id} value={b.id.toString()}>
                  {b.brand} — {b.product}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      {shots.length === 0 ? (
        <p className="py-12 text-center text-sm text-muted-foreground">
          No shots logged yet.
        </p>
      ) : (
        <div className="space-y-3">
          {shots.map((shot) => {
            const bean = beanMap.get(shot.bean_id);
            const reasonLabel =
              REASON_LABELS[shot.reason_code] ?? shot.reason_code;
            const variant =
              REASON_VARIANT[shot.reason_code] ?? "secondary";

            return (
              <Card key={shot.id}>
                <CardHeader className="p-4 pb-2">
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-base">
                      {bean
                        ? `${bean.brand} — ${bean.product}`
                        : `Bean #${shot.bean_id}`}
                    </CardTitle>
                    <Badge variant={variant} className="shrink-0 text-xs">
                      {reasonLabel}
                    </Badge>
                  </div>
                  <CardDescription className="text-xs">
                    {formatDate(shot.created_at)}
                  </CardDescription>
                </CardHeader>
                <CardContent className="px-4 pb-4 pt-0">
                  <div className="grid grid-cols-4 gap-2 text-sm">
                    <div>
                      <span className="text-xs text-muted-foreground">
                        Dose
                      </span>
                      <p className="font-medium">{shot.dose_g}g</p>
                    </div>
                    <div>
                      <span className="text-xs text-muted-foreground">
                        Yield
                      </span>
                      <p className="font-medium">{shot.yield_g}g</p>
                    </div>
                    <div>
                      <span className="text-xs text-muted-foreground">
                        Time
                      </span>
                      <p className="font-medium">{shot.time_s}s</p>
                    </div>
                    <div>
                      <span className="text-xs text-muted-foreground">
                        Grind
                      </span>
                      <p className="font-medium">
                        {shot.grind_setting_native}
                      </p>
                    </div>
                  </div>
                  {shot.taste && (
                    <p className="mt-2 text-xs text-muted-foreground">
                      Taste: {shot.taste.charAt(0) + shot.taste.slice(1).toLowerCase()}
                      {shot.intensity
                        ? ` (${shot.intensity.toLowerCase()})`
                        : ""}
                    </p>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
