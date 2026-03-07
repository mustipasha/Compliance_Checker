module.exports = {
    apps: [
        {
            name: 'cc-backend',
            script: 'python3',
            args: 'main.py',
            cwd: './backend',
            interpreter: './backend/.venv/bin/python',
            autorestart: true,
            env: {
                NODE_ENV: 'development',
                PORT: 8000
            }
        },
        {
            name: 'cc-frontend',
            script: 'npm',
            args: 'run dev',
            cwd: './frontend',
            autorestart: true,
            env: {
                VITE_PORT: 5173
            }
        }
    ]
};
