import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Homepage from "./components/Homepage";
import Dashboard from "./components/Dashboard";
import LeadScraper from "./components/LeadScraper";
import Results from "./components/Results";
import AutomationDashboard from "./components/AutomationDashboard";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/scraper" element={<LeadScraper />} />
          <Route path="/results" element={<Results />} />
          <Route path="/automation" element={<AutomationDashboard />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;