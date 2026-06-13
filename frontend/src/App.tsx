import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { LogShot } from "@/pages/LogShot";
import { Suggestion } from "@/pages/Suggestion";
import { Setup } from "@/pages/Setup";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<LogShot />} />
          <Route path="suggestion" element={<Suggestion />} />
          <Route path="setup" element={<Setup />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
