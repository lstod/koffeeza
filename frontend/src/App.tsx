import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { Layout } from "@/components/Layout";
import { LogShot } from "@/pages/LogShot";
import { Suggestion } from "@/pages/Suggestion";
import { History } from "@/pages/History";
import { Setup } from "@/pages/Setup";
import { UserPicker } from "@/pages/UserPicker";

function AppRoutes() {
  const { user } = useAuth();

  if (!user) {
    return <UserPicker />;
  }

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<LogShot />} />
        <Route path="suggestion" element={<Suggestion />} />
        <Route path="history" element={<History />} />
        <Route path="setup" element={<Setup />} />
      </Route>
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
