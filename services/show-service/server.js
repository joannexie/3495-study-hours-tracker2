import express from "express";
import session from "express-session";
import cookieParser from "cookie-parser";
import axios from "axios";
import { MongoClient } from "mongodb";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, "public")));

app.use(
  session({
    secret: process.env.SESSION_SECRET || "dev_session",
    resave: false,
    saveUninitialized: false
  })
);

const PORT = process.env.PORT || 4000;
const AUTH_URL = process.env.AUTH_URL || "http://auth-service:3000";
const MONGO_URL = process.env.MONGO_URL || "mongodb://mongo:27017";
const MONGO_DB = process.env.MONGO_DB || "studytracker";

let mongoClient;
async function getAnalyticsCollection() {
  if (!mongoClient) {
    mongoClient = new MongoClient(MONGO_URL);
    await mongoClient.connect();
  }
  return mongoClient.db(MONGO_DB).collection("analytics");
}

async function requireLogin(req) {
  const token = req.session.token;
  if (!token) return { ok: false };

  try {
    const r = await axios.post(
      `${AUTH_URL}/verify`,
      {},
      { headers: { Authorization: `Bearer ${token}` }, timeout: 3000 }
    );
    return { ok: true, username: r.data.username };
  } catch (e) {
    return { ok: false };
  }
}

app.get("/", async (req, res) => {
  const auth = await requireLogin(req);
  if (!auth.ok) return res.redirect("/login");
  res.redirect("/results");
});

app.get("/login", (req, res) => {
  res.render("login", { error: null });
});

app.post("/login", async (req, res) => {
  const { username, password } = req.body || {};
  try {
    const r = await axios.post(`${AUTH_URL}/login`, { username, password }, { timeout: 3000 });
    req.session.token = r.data.token;
    req.session.username = r.data.username;
    res.redirect("/results");
  } catch (e) {
    res.status(401).render("login", { error: "Invalid login. Try again." });
  }
});

app.get("/logout", (req, res) => {
  req.session.destroy(() => res.redirect("/login"));
});

app.get("/results", async (req, res) => {
  const auth = await requireLogin(req);
  if (!auth.ok) return res.redirect("/login");

  const col = await getAnalyticsCollection();
  const latest = await col.find().sort({ generated_at: -1 }).limit(1).toArray();
  const doc = latest[0] || null;

  res.render("results", { username: auth.username, doc });
});

app.get("/api/latest", async (req, res) => {
  const auth = await requireLogin(req);
  if (!auth.ok) return res.status(401).json({ error: "not logged in" });

  const col = await getAnalyticsCollection();
  const latest = await col.find().sort({ generated_at: -1 }).limit(1).toArray();
  res.json(latest[0] || {});
});

app.listen(PORT, () => console.log(`show-service listening on ${PORT}`));
