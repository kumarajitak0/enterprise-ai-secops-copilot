import { Outlet } from "react-router-dom";
import TopNav from "./TopNav";

export default function AppShell() {
  return (
    <div className="app-root">
      <div className="app-container">
        <TopNav />
        <Outlet />
      </div>
    </div>
  );
}