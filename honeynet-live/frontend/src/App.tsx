import { Navigate, Route, Routes } from "react-router-dom";
import { getToken } from "./services/api";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import LiveAttacks from "./pages/LiveAttacks";
import AttackMap from "./pages/AttackMap";
import Attackers from "./pages/Attackers";
import AttackerDetail from "./pages/AttackerDetail";
import Credentials from "./pages/Credentials";
import Commands from "./pages/Commands";
import Malware from "./pages/Malware";
import Clusters from "./pages/Clusters";
import Blocklist from "./pages/Blocklist";
import Health from "./pages/Health";
import Settings from "./pages/Settings";

function Guard({ children }: { children: React.ReactNode }) {
  if (!getToken()) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <Guard>
            <Layout />
          </Guard>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="live" element={<LiveAttacks />} />
        <Route path="map" element={<AttackMap />} />
        <Route path="attackers" element={<Attackers />} />
        <Route path="attackers/:ip" element={<AttackerDetail />} />
        <Route path="credentials" element={<Credentials />} />
        <Route path="commands" element={<Commands />} />
        <Route path="malware" element={<Malware />} />
        <Route path="ml" element={<Clusters />} />
        <Route path="blocklist" element={<Blocklist />} />
        <Route path="health" element={<Health />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}
