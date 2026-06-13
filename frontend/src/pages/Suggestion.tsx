import { useLocation, useNavigate, Navigate } from "react-router-dom";
import { ArrowDown, ArrowUp, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import type { ShotSuggestionResponse } from "@/lib/types";

const CONFIDENCE_VARIANT: Record<string, "default" | "secondary" | "outline"> =
  {
    HIGH: "default",
    MEDIUM: "secondary",
    LOW: "outline",
  };

export function Suggestion() {
  const location = useLocation();
  const navigate = useNavigate();
  const suggestion = (
    location.state as { suggestion?: ShotSuggestionResponse } | null
  )?.suggestion;

  if (!suggestion) {
    return <Navigate to="/" replace />;
  }

  const isDialedIn = suggestion.direction === null;

  return (
    <div className="flex min-h-[calc(100svh-4rem)] flex-col items-center justify-center p-4">
      {isDialedIn ? (
        <Card className="w-full">
          <CardHeader className="items-center text-center">
            <CheckCircle2 className="mb-2 h-14 w-14 text-green-500" />
            <CardTitle className="text-2xl">Dialed In!</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-center">
            <p className="text-muted-foreground">{suggestion.rationale}</p>
            <Badge variant={CONFIDENCE_VARIANT[suggestion.confidence]}>
              {suggestion.confidence}
            </Badge>
          </CardContent>
        </Card>
      ) : (
        <Card className="w-full">
          <CardHeader className="items-center text-center">
            <div className="mb-2">
              {suggestion.direction === "FINER" ? (
                <ArrowDown className="h-12 w-12 text-blue-400" />
              ) : (
                <ArrowUp className="h-12 w-12 text-orange-400" />
              )}
            </div>
            <CardTitle className="text-xl leading-relaxed">
              {suggestion.instruction}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-center">
              <Badge variant={CONFIDENCE_VARIANT[suggestion.confidence]}>
                {suggestion.confidence} confidence
              </Badge>
            </div>
            <Separator />
            <p className="text-sm leading-relaxed text-muted-foreground">
              {suggestion.rationale}
            </p>
          </CardContent>
        </Card>
      )}

      <Button
        className="mt-6 h-12 w-full text-base"
        onClick={() => navigate("/")}
      >
        Log another shot
      </Button>
    </div>
  );
}
