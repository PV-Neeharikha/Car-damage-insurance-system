import { useState } from "react";
import { useNavigate } from "react-router-dom";

import "./UploadPage.css";

function SignupPage() {

    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const handleSignup = async () => {

        if (!username.trim()) {
            alert("Username is required");
            return;
        }

        if (!email.trim()) {
            alert("Email is required");
            return;
        }

        if (!password.trim()) {
            alert("Password is required");
            return;
        }

        const emailRegex =
            /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(email)) {
            alert("Please enter a valid email address");
            return;
        }

        if (password.length < 8) {
            alert("Password must be at least 8 characters");
            return;
        }

        try {

            const response = await fetch(
                "http://localhost:5000/signup",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        username,
                        email,
                        password
                    })
                }
            );

            const data = await response.json();

            if (data.success) {

                alert("Account Created Successfully!");

                navigate("/");

            } else {

                alert(data.message);
            }

        } catch (error) {

            console.error(error);
            alert("Server Error");
        }
    };

    return (

        <div className="upload-page1">

            <div className="inspection-shell">

                <div className="auth-container">

                    <div className="auth-card">

                        <h1 className="auth-title">
                            Create Account
                        </h1>

                        <p className="auth-subtitle">
                            Start your AI vehicle inspection journey
                        </p>

                        <input
                            className="auth-input"
                            type="text"
                            placeholder="Username"
                            value={username}
                            onChange={(e) =>
                                setUsername(e.target.value)
                            }
                        />

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
                            onClick={handleSignup}
                        >
                            Create Account
                        </button>

                        <p
                            className="auth-link"
                            onClick={() => navigate("/")}
                        >
                            Already have an account?
                            <span> Login</span>
                        </p>

                    </div>

                </div>

            </div>

        </div>
    );
}

export default SignupPage;