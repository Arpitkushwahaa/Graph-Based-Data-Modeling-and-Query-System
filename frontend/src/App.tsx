import React, { useState, useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import axios from 'axios';
import { Send, LayoutTemplate } from 'lucide-react';
import './App.css';

interface Node {
  id: string;
  label: string;
  [key: string]: any;
}

interface Link {
  source: string;
  target: string;
  label: string;
}

interface Message {
  sender: 'user' | 'bot';
  text: string;
}

const App: React.FC = () => {
  const [graphData, setGraphData] = useState<{ nodes: Node[]; links: Link[] }>({ nodes: [], links: [] });
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputVal, setInputVal] = useState('');
  const [loading, setLoading] = useState(false);
  const fgRef = useRef<any>();

  useEffect(() => {
    // Fetch initial graph
    axios.get('http://localhost:8000/graph')
      .then(res => setGraphData(res.data))
      .catch(err => console.error("Error fetching graph:", err));
  }, []);

  const handleSend = async () => {
    if (!inputVal.trim()) return;
    
    const userMsg = inputVal;
    setMessages(prev => [...prev, { sender: 'user', text: userMsg }]);
    setInputVal('');
    setLoading(true);

    try {
      const res = await axios.post('http://localhost:8000/query', { question: userMsg });
      setMessages(prev => [...prev, { sender: 'bot', text: res.data.answer }]);
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'bot', text: "Sorry, I had an issue processing that query." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen font-sans bg-gray-50 text-gray-900 overflow-hidden">
      
      {/* Visual Graph Section */}
      <div className="flex-1 border-r border-gray-200 relative overflow-hidden">
        <div className="absolute top-4 left-4 z-10 bg-white p-3 rounded-md shadow-md flex items-center gap-2">
           <LayoutTemplate size={20} />
           <span className="font-semibold">Graph Viewer</span>
        </div>
        <ForceGraph2D
          ref={fgRef}
          graphData={graphData}
          nodeAutoColorBy="label"
          nodeLabel={(node: any) => `${node.label}: ${node.id}`}
          linkDirectionalArrowLength={3.5}
          linkDirectionalArrowRelPos={1}
          linkColor={() => '#ccc'}
        />
      </div>

      {/* Chat Interface Section */}
      <div className="w-1/3 min-w-[300px] flex flex-col bg-white overflow-hidden">
        <div className="p-4 border-b border-gray-100 bg-gray-50 flex flex-col">
          <h2 className="text-lg font-bold">Chat with Graph</h2>
          <span className="text-sm text-gray-500">Order to Cash Assistant</span>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div className="bg-gray-100 p-3 rounded-lg w-max max-w-sm text-sm self-start">
            Hi! I can help you analyze the Order to Cash process. Ask me anything related to orders, invoices, or payments.
          </div>
          
          {messages.map((msg, idx) => (
            <div key={idx} className={`p-3 rounded-lg w-max max-w-sm text-sm ${msg.sender === 'user' ? 'bg-black text-white self-end ml-auto' : 'bg-gray-100 text-black self-start'}`}>
              {msg.text}
            </div>
          ))}
          {loading && (
             <div className="bg-gray-100 p-3 rounded-lg w-max max-w-sm text-sm self-start animate-pulse">
               Thinking...
             </div>
          )}
        </div>

        <div className="p-4 border-t border-gray-200">
           <div className="flex items-center gap-2 bg-gray-50 p-2 rounded-md border border-gray-200 shadow-sm focus-within:ring-2 focus-within:ring-blue-500">
             <input 
               type="text" 
               className="flex-1 bg-transparent p-2 outline-none text-sm placeholder-gray-500" 
               placeholder="Analyze anything..."
               value={inputVal}
               onChange={e => setInputVal(e.target.value)}
               onKeyDown={e => e.key === 'Enter' && handleSend()}
             />
             <button 
               onClick={handleSend} 
               disabled={loading || !inputVal.trim()}
               className="p-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 disabled:opacity-50"
             >
               <Send size={16} />
             </button>
           </div>
        </div>
      </div>

    </div>
  );
};

export default App;
