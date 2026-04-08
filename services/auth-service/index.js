import express from "express";
import cors from "cors";
import jwt from "jsonwebtoken";
import { USERS } from "./users.js";

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || "dev_secret";

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "auth-service" });
});

app.post("/login", (req, res) => {
  const { username, password } = req.body || {};
  if (!username || !password) {
    return res.status(400).json({ error: "username and password required" });
  }

  const ok = USERS.find(u => u.username === username && u.password === password);
  if (!ok) return res.status(401).json({ error: "invalid credentials" });

  const token = jwt.sign({ sub: username }, JWT_SECRET, { expiresIn: "2h" });
  res.json({ token, username });
});

app.post("/verify", (req, res) => {
  const auth = req.headers.authorization || "";
  const token = auth.startsWith("Bearer ") ? auth.slice(7) : null;
  if (!token) return res.status(401).json({ valid: false, error: "missing token" });

  try {
    const payload = jwt.verify(token, JWT_SECRET);
    res.json({ valid: true, username: payload.sub });
  } catch (e) {
    res.status(401).json({ valid: false, error: "invalid token" });
  }
});

app.listen(PORT, () => console.log(`auth-service listening on ${PORT}`));
