import { useState } from 'react';

function App() {
    const [logs, setLogs] = useState([]);
    const [isGenerating, setIsGenerating] = useState(false);
    const [topic, setTopic] = useState(""); // New state for user input

    const startPipeline = () => {
        if (!topic.trim()) {
            alert("Please enter a topic to research!");
            return;
        }

        setLogs([]);
        setIsGenerating(true);
        
        // Pass the encoded topic safely into the URL query
        const url = `http://localhost:5000/api/generate-article?topic=${encodeURIComponent(topic)}`;
        const eventSource = new EventSource(url);
        
        eventSource.onmessage = (event) => {
            if (event.data === '[PROCESS_COMPLETE]') {
                eventSource.close();
                setIsGenerating(false);
            } else {
                setLogs((prev) => [...prev, event.data]);
            }
        };

        eventSource.onerror = (error) => {
            console.error('SSE Error:', error);
            eventSource.close();
            setIsGenerating(false);
        };
    };

    return (
        <div className="min-h-screen bg-slate-950 text-slate-300 p-8 flex flex-col items-center">
            <div className="w-full max-w-4xl">
                <div className="flex flex-col mb-8 gap-4">
                    <h1 className="text-3xl font-bold text-white">Multi-Agent Content Pipeline</h1>
                    
                    {/* New Input Form */}
                    <div className="flex gap-4">
                        <input 
                            type="text" 
                            placeholder="Enter a topic to research..." 
                            className="flex-1 px-4 py-2 bg-slate-900 border border-slate-700 rounded text-white focus:outline-none focus:border-indigo-500"
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            disabled={isGenerating}
                        />
                        <button 
                            onClick={startPipeline} 
                            disabled={isGenerating || !topic.trim()}
                            className={`px-6 py-2 rounded font-semibold text-white transition-colors 
                                ${isGenerating || !topic.trim() ? 'bg-slate-700 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-500'}`}
                        >
                            {isGenerating ? 'Agents Working...' : 'Start Research'}
                        </button>
                    </div>
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 min-h-[400px] font-mono text-sm shadow-xl overflow-y-auto">
                    {logs.length === 0 && !isGenerating && (
                        <p className="text-slate-500 italic">Enter a topic and click start to boot up the agents...</p>
                    )}
                    
                    <div className="space-y-2">
                        {logs.map((log, i) => {
                            let textColor = "text-slate-300";
                            if (log.includes("[System]")) textColor = "text-fuchsia-400";
                            if (log.includes("[Researcher]")) textColor = "text-blue-400";
                            if (log.includes("[Writer]")) textColor = "text-emerald-400";
                            if (log.includes("[Editor]")) textColor = "text-amber-400";
                            if (log.includes("[ERROR]")) textColor = "text-red-400";
                            
                            return <div key={i} className={textColor}>{log}</div>;
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default App;