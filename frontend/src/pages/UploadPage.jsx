import { useState } from "react";
import { useNavigate,Link } from "react-router-dom";
import "./UploadPage.css";

function App() {

  const [front, setFront] = useState(null);
  const [back, setBack] = useState(null);
  const [left, setLeft] = useState(null);
  const [right, setRight] = useState(null);
  const [top, setTop] = useState(null);
  const [policy, setPolicy] = useState("");
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const handleUpload = async () => {
    if (!front || !back || !left || !right) 
    {
        alert("Please upload Front, Back, Left and Right images");
        return;
    }

    if (!policy) 
    {
        alert("Please select a policy");
        return;
    }
  const formData = new FormData();

  formData.append("front", front);
  formData.append("back", back);
  formData.append("left", left);
  formData.append("right", right);

  if (top) {
    formData.append("top", top);
  }

  formData.append("policy_type", policy);

  try {
    setLoading(true);
    const response = await fetch(
      "http://127.0.0.1:5000/classify",
      {
        method: "POST",
        body: formData
      }
    );

    const data = await response.json();
    navigate("/results", {state: {results: data}});

  } catch(error) {
    setLoading(false);
    console.error(error);

  }
  finally {
  setLoading(false);
}
};
  return (
        <div className="upload-page1">
            <div className="inspection-shell">
            <div className="hero-card1">
                <h1 className="hero-title1"> AI Vehicle Damage Assessment</h1>
                <p className="hero-subtitle1">Insurance-Oriented Multi-View Vehicle Inspection Platform</p>
            </div>
            <div className="upload-grid1">
                <div className="upload-card1">
                    <h3> {front ? "✓ Front View" : "Front View"}</h3>
                    <label className="file-upload-box1">
                        <input type="file" className="hidden-input1" onChange={(e) => setFront(e.target.files[0])} />
                        <p>  {front ? "Image Uploaded" : "Click to upload image"}</p>
                        {front && (
                            <div className="file-name1">
                                {front.name}
                            </div>
                        )}
                    </label>
                </div>
                <div className="upload-card1">
                    <h3> {back ? "✓ Rear View" : "Rear View"}</h3>
                    <label className="file-upload-box1">
                        <input type="file" className="hidden-input1" onChange={(e) => setBack(e.target.files[0])} />
                        <p>  {back ? "Image Uploaded" : "Click to upload image"}</p>
                        {back && (
                            <div className="file-name1">
                                {back.name}
                            </div>
                        )}
                    </label>
                </div>
               <div className="upload-card1">
                    <h3> {left ? "✓ Left View" : "Left View"}</h3>
                    <label className="file-upload-box1">
                        <input type="file" className="hidden-input1" onChange={(e) => setLeft(e.target.files[0])} />
                        <p>  {left ? "Image Uploaded" : "Click to upload image"}</p>
                        {left && (
                            <div className="file-name1">
                                {left.name}
                            </div>
                        )}
                    </label>
                </div>

                <div className="upload-card1">
                    <h3> {right ? "✓ Right View" : "Right View"}</h3>
                    <label className="file-upload-box1">
                        <input type="file" className="hidden-input1" onChange={(e) => setRight(e.target.files[0])} />
                        <p>  {right ? "Image Uploaded" : "Click to upload image"}</p>
                        {right && (
                            <div className="file-name1">
                                {right.name}
                            </div>
                        )}
                    </label>
                </div>
                <div className="upload-card1">
                    <h3> {top ? "✓ Top View" : "Top View"}</h3>
                    <label className="file-upload-box1">
                        <input type="file" className="hidden-input1" onChange={(e) => setTop(e.target.files[0])} />
                        <p>  {top ? "Image Uploaded" : "Click to upload image"}</p>
                        {top && (
                            <div className="file-name1">
                                {top.name}
                            </div>
                        )}
                    </label>
                </div>
                <div className="upload-card1">
                    <h3> Insurance Policy</h3>

                    <select
                        value={policy}
                        onChange={(e) => setPolicy(e.target.value)}
                    >
                        <option value="">
                            Select Policy
                        </option>

                        <option value="third_party">
                            Third Party
                        </option>

                        <option value="policy_a">
                            Policy A
                        </option>

                        <option value="policy_b">
                            Policy B
                        </option>

                        <option value="policy_c">
                            Policy C
                        </option>

                    </select>
                </div>

            </div>

            <button
                className="analyze-btn1"
                onClick={handleUpload}
                disabled={loading}
            >
                {loading
                    ? "Analyzing Vehicle..."
                    : "Start AI Inspection"}
            </button>
            <Link to="/">
            <button className="action-btn">
                    Logout
            </button>
            </Link>
            </div>
        </div>

);
}

export default App;