import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { LogShot } from "@/pages/LogShot";
import { Suggestion } from "@/pages/Suggestion";
import { History } from "@/pages/History";
import { Setup } from "@/pages/Setup";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<LogShot />} />
          <Route path="suggestion" element={<Suggestion />} />
          <Route path="history" element={<History />} />
          <Route path="setup" element={<Setup />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
