import { Outlet } from "react-router-dom";
import { BottomNav } from "./BottomNav";

export function Layout() {
  return (
    <div className="mx-auto min-h-svh max-w-lg pb-16">
      <Outlet />
      <BottomNav />
    </div>
  );
}
