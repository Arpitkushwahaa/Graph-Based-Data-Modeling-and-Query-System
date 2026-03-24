import React, { useState, useEffect, useRef, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import axios from 'axios';
import { Send, LayoutTemplate, X } from 'lucide-react';
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
  const [highlightNodes, setHighlightNodes] = useState<Set<string>>(new Set());
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const fgRef = useRef<any>(null);

  useEffect(() => {
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
    setHighlightNodes(new Set()); // Reset highlights on new query

    try {
      const res = await axios.post('http://localhost:8000/query', { question: userMsg });
      setMessages(prev => [...prev, { sender: 'bot', text: res.data.answer }]);
      if (res.data.data && Array.isArray(res.data.data)) {
        setHighlightNodes(new Set(res.data.data));
      }
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'bot', text: "Sorry, I had an issue processing that query." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleNodeClick = useCallback((node: Node) => {
    setSelectedNode(node);
    // Center graph on node
    fgRef.current.centerAt(node.x, node.y, 1000);
    fgRef.current.zoom(4, 1000);
  }, []);

  return (
    <div className="flex h-screen w-screen font-sans bg-gray-50 text-gray-900 overflow-hidden">
      
      {/* Visual Graph Section */}
      <div className="flex-1 border-r border-gray-200 relative overflow-hidden">
        <div className="absolute top-4 left-4 z-10 bg-white p-3 rounded-md shadow-md flex items-center gap-2">
           <LayoutTemplate size={20} />
           <span className="font-semibold text-sm">Order-to-Cash Explorer</span>
        </div>
        
        {/* Node Detail Popup */}
        {selectedNode && (
          <div className="absolute top-20 left-4 z-10 bg-white w-72 rounded-lg py-4 px-5 shadow-xl border border-gray-200">
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-bold text-gray-800 text-lg">{selectedNode.label || 'Entity'}</h3>
              <button onClick={() => setSelectedNode(null)} className="text-gray-400 hover:text-gray-700">
                 <X size={18} />
              </button>
            </div>
            
            <div className="text-sm space-y-2 text-gray-700">
              <div className="flex justify-between">
                <span className="font-semibold text-gray-500">ID:</span>
                <span>{selectedNode.id}</span>
              </div>
              {Object.keys(selectedNode)
                .filter(k => !['id', 'label', 'x', 'y', 'vx', 'vy', 'index', 'color'].includes(k))
                .map(key => (
                  <div key={key} className="flex justify-between border-t border-gray-100 pt-2 mt-2">
                    <span className="font-semibold text-gray-500 capitalize">{key}:</span>
                    <span className="text-right ml-4 break-all">{String(selectedNode[key])}</span>
                  </div>
              ))}
            </div>
          </div>
        )}

        <ForceGraph2D
          ref={fgRef}
          graphData={graphData}
          nodeAutoColorBy="label"
          nodeColor={node => highlightNodes.has(node.id as string) ? '#ff0000' : (node.color as string)}
          nodeRelSize={highlightNodes.size > 0 ? 6 : 4}
          nodeLabel={(node: any) => `${node.label}: ${node.id}`}
          onNodeClick={handleNodeClick}
          linkDirectionalArrowLength={3.5}
          linkDirectionalArrowRelPos={1}
          linkColor={() => '#d1d5db'}
        />
      </div>

      {/* Chat Interface Section */}
      <div className="w-1/3 min-w-[350px] flex flex-col bg-white overflow-hidden shadow-lg z-20">
        <div className="p-5 border-b border-gray-100 bg-[#f8f9fa] flex flex-col">
          <h2 className="text-lg font-bold">Chat with Graph</h2>
          <span className="text-sm text-gray-500">Analytics Agent</span>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div className="bg-gray-100 p-3 rounded-xl w-max max-w-[90%] text-sm self-start whitespace-pre-wrap">
            Hi! I can help you analyze the Order to Cash process. Ask me questions like:<br/><br/>
            • "Trace the flow for Order O1001"<br/>
            • "Which products have the highest invoices?"<br/>
            • "Are there any deliveries without an invoice?"
          </div>
          
          {messages.map((msg: Message, idx: number) => (
            <div key={idx} className={`p-3 rounded-xl w-max max-w-[90%] text-sm ${msg.sender === 'user' ? 'bg-gray-800 text-white self-end ml-auto' : 'bg-gray-100 text-black self-start'}`}>
              {msg.text}
            </div>
          ))}
          {loading && (
             <div className="bg-gray-100 p-3 rounded-xl w-max text-sm self-start flex items-center gap-2">
               <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
               <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
               <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
             </div>
          )}
        </div>

        <div className="p-4 border-t border-gray-200">
           <div className="flex items-center gap-2 bg-[#f8f9fa] p-2 rounded-xl border border-gray-200 focus-within:ring-2 focus-within:ring-gray-300 transition-all">
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
               className="p-2.5 bg-gray-800 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 transition-colors"
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
