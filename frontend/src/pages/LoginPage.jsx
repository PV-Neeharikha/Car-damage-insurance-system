import { useState } from "react";
import { useNavigate } from "react-router-dom";

import "./UploadPage.css";

function LoginPage() {

    const navigate = useNavigate();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const handleLogin = async () => {

        if (!email.trim()) {
            alert("Please enter your email");
            return;
        }

        if (!password.trim()) {
            alert("Please enter your password");
            return;
        }

        try {

            const response = await fetch(
                "http://localhost:5000/login",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        email,
                        password
                    })
                }
            );

            const data = await response.json();

            if (data.success) {

                localStorage.setItem(
                    "username",
                    data.username
                );

                navigate("/upload");

            } else {

                alert(data.message);
            }

        } catch (error) {

            console.error("Login Error:", error);
            alert("Server Error");
        }
    };

    return (

        <div className="upload-page1">

            <div className="inspection-shell">

                <div className="auth-container">

                    <div className="auth-card">

                        <h1 className="auth-title">
                            Car Damage Detection
                        </h1>

                        <p className="auth-subtitle">
                            Login to continue
                        </p>

                        <input
                            className="auth-input"
                            type="email"
                            placeholder="Email Address"
                            value={email}
                            onChange={(e) =>
                                setEmail(e.target.value)
                            }
                        />

                        <input
                            className="auth-input"
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) =>
                                setPassword(e.target.value)
                            }
                        />

                        <button
                            className="auth-btn"
                            onClick={handleLogin}
                        >
                            Login
                        </button>

                        <p
                            className="auth-link"
                            onClick={() => navigate("/signup")}
                        >
                            Don't have an account?
                            <span> Sign Up</span>
                        </p>

                    </div>

                </div>

            </div>

        </div>
    );
}

export default LoginPage;