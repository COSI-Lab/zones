require('dotenv').config();

const express = require("express");
const { exec } = require("child_process");
const app = express();
app.use(express.json())

app.post('/', (req, res) => {
    if (req.body.secret != process.env.SECRET) {
        res.sendStatus(403);
    }

    exec("cd .. && git reset --hard && git pull");

    exec("systemctl reload nsd", (error, _, _) => {
        if (error) {
            res.sendStatus(500);
        } else {
            res.sendStatus(200);
        }
    });
})

app.listen(80, () => {
    console.log(`Example app listening at http://localhost:80`)
})