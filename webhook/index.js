require('dotenv').config();

const express = require("express");
const { exec } = require("child_process");
const app = express();
app.use(express.json())

app.post('/', (req, res) => {
    if (req.get("X-Gitlab-Token") != process.env.SECRET) {
        res.sendStatus(403);
        return;
    }

    console.log("pull and reload changes");

    exec("cd .. && git reset --hard && git pull");

    exec("systemctl reload nsd", (error, _stdout, _stderr) => {
        if (error) {
            res.sendStatus(500);
            console.log("failed")
        } else {
            res.sendStatus(200);
            console.log("success")
        }
    });
})

const PORT = 8080
app.listen(PORT, "0.0.0.0", () => {
    console.log(`GitLab webhook listener running at http://0.0.0.0:${PORT}`)
})