import { BrowserRouter, Routes, Route } from "react-router-dom";
import AgentPage from "./pages/AgentPage";

/**
 * App — root routing configuration.
 * Add new routes here as the app scales in future phases.
 */
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AgentPage />} />
      </Routes>
    </BrowserRouter>
  );
}
