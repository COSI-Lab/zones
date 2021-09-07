require('dotenv').config();

const express = require("express");
const { exec } = require("child_process");
const app = express();
app.use(express.json())

app.post('/', (req, res) => {
    if (req.body.secret != process.env.SECRET) {
        res.sendStatus(403);
        return;
    }

    console.log("pull and reload changes");

    exec("cd .. && git reset --hard && git pull");

    exec("systemctl reload nsd", (error, _stdout, _stderr) => {
        if (error) {
            res.sendStatus(500);
        } else {
            res.sendStatus(200);
        }
    });
})

const PORT = 8080
app.listen(PORT, () => {
    console.log(`Example app listening at http://localhost:${PORT}`)
})