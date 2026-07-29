import express from 'express';
import cors from 'cors';
import { spawn } from 'child_process';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

app.get('/api/generate-article', (req, res) => {
    // 1. Grab the topic from the frontend URL, fallback to default if missing
    const topic = req.query.topic || "Zero-Knowledge Proofs";

    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    
    // 2. Pass the topic as the final argument in the spawn array
    const pythonProcess = spawn('uv', ['run', 'python', '-u', 'pipeline.py', topic], {
        env: { ...process.env, PYTHONUNBUFFERED: '1' }
    });
    
    pythonProcess.stdout.on('data', (data) => {
        const text = data.toString();
        // Split the text by newlines so we don't break the SSE protocol
        const lines = text.split('\n');
        for (const line of lines) {
            if (line.trim()) {
                res.write(`data: ${line}\n\n`);
            }
        }
    });

    pythonProcess.stderr.on('data', (data) => {
        const text = data.toString().trim();
        if (text) {
             res.write(`data: [ERROR] ${text}\n\n`);
        }
    });

    pythonProcess.on('close', () => {
        res.write(`data: [PROCESS_COMPLETE]\n\n`);
        res.end();
    });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server streaming on http://localhost:${PORT}`);
});