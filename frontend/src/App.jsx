import { BrowserRouter, Routes, Route } from "react-router-dom";

import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import UploadPage from "./pages/UploadPage";
import ResultsPage from "./pages/ResultsPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Login Page */}
        <Route path="/" element={<LoginPage />} />

        {/* Upload Page */}
        <Route path="/upload" element={<UploadPage />} />

        {/* Results Page */}
        <Route path="/results" element={<ResultsPage />} />

        {/* Signup Page */}
        <Route path="/signup" element={<SignupPage />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;