import React, { useState, useEffect, useRef, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import axios from 'axios';
import { Columns, Minimize2, Layers, User } from 'lucide-react';
import './App.css';

interface Node {
  id: string;
  label: string;
  type?: string;
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
  const [messages, setMessages] = useState<Message[]>([
    { sender: 'bot', text: 'Hi! I can help you analyze the **Order to Cash** process.' }
  ]);
  const [inputVal, setInputVal] = useState('');
  const [loading, setLoading] = useState(false);
  const [highlightNodes, setHighlightNodes] = useState<Set<string>>(new Set());
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const fgRef = useRef<any>(null);

  useEffect(() => {
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    axios.get(`${apiUrl}/graph`)
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
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const res = await axios.post(`${apiUrl}/query`, { question: userMsg });
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
    if(fgRef.current) {
      fgRef.current.centerAt(node.x, node.y, 1000);
      fgRef.current.zoom(4, 1000);
    }
  }, []);

  return (
    <div className="flex flex-col h-screen w-screen font-sans bg-white text-gray-900 overflow-hidden">
      
      {/* Top Header */}
      <div className="flex items-center px-4 py-3 border-b border-gray-100 z-20 shadow-sm relative">
        <Columns size={18} className="text-gray-500 mr-4" />
        <div className="text-gray-400 text-[15px] flex items-center">
          Mapping <span className="mx-2 text-gray-300">/</span> <span className="text-gray-900 font-semibold">Order to Cash</span>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Visual Graph Section */}
        <div className="flex-1 relative overflow-hidden bg-[#fafafa]">
          
          {/* Floating Controls */}
          <div className="absolute top-4 left-4 z-10 flex items-center gap-2">
            <button className="flex items-center gap-2 bg-white px-3 py-2 rounded shadow-sm border border-gray-200 text-xs font-semibold hover:bg-gray-50 transition-colors">
              <Minimize2 size={14} />
              Minimize
            </button>
            <button className="flex items-center gap-2 bg-black text-white px-3 py-2 rounded shadow-sm text-xs font-semibold hover:bg-gray-800 transition-colors">
              <Layers size={14} />
              Hide Granular Overlay
            </button>
          </div>
          
          {/* Node Detail Popup */}
          {selectedNode && (
            <div className="absolute top-20 left-4 z-10 bg-white w-[320px] rounded-xl py-4 px-5 shadow-[0_8px_30px_rgb(0,0,0,0.12)] border border-gray-100">
              <h3 className="font-bold text-gray-900 text-base mb-3">{selectedNode.label || 'Entity'}</h3>
              
              <div className="text-xs space-y-1 text-gray-600 mb-3 pb-3 border-b border-gray-100">
                <div><span className="font-medium text-gray-500">ID:</span> {selectedNode.id}</div>
                {Object.keys(selectedNode)
                  .filter(k => !['id', 'label', 'x', 'y', 'vx', 'vy', 'index', 'color', 'Connections'].includes(k))
                  .slice(0, 10) // Limit rows shown for readability
                  .map(key => (
                    <div key={key} className="break-all">
                      <span className="font-medium text-gray-500 capitalize">{key}:</span> {String(selectedNode[key])}
                    </div>
                ))}
              </div>
              
              <div className="text-[11px] text-gray-400 italic mb-2">Additional fields hidden for readability</div>
              <div className="text-xs font-medium text-gray-600">Connections: {selectedNode.Connections || 0}</div>
            </div>
          )}

          <ForceGraph2D
            ref={fgRef}
            graphData={graphData}
            nodeColor={(node: any) => highlightNodes.has(node.id as string) ? '#22c55e' : (node.label === 'Customer' || node.label === 'Order' ? '#fca5a5' : '#60a5fa')}
            nodeRelSize={2.5}
            nodeLabel={(node: any) => `${node.label}: ${node.id}`}
            onNodeClick={handleNodeClick}
            linkWidth={0.5}
            linkColor={() => '#bae6fd'}
            linkDirectionalArrowLength={2}
            linkDirectionalArrowRelPos={1}
            backgroundColor="#ffffff"
          />
        </div>

        {/* Chat Interface Section */}
        <div className="w-[380px] flex flex-col bg-white overflow-hidden border-l border-gray-200 z-20 shadow-xl">
          
          <div className="p-4 border-b border-gray-100">
            <h2 className="text-[15px] font-bold text-gray-900">Chat with Graph</h2>
            <span className="text-[12px] text-gray-500">Order to Cash</span>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-7">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
                
                {msg.sender === 'user' && (
                  <div className="flex flex-col items-end w-full">
                    <div className="flex items-center gap-2 mb-1 justify-end w-full mr-2">
                       <span className="font-bold text-xs text-gray-900">You</span>
                       <div className="w-7 h-7 rounded-full bg-gray-300 flex items-center justify-center text-white">
                         <User size={14} />
                       </div>
                    </div>
                    <div className="bg-[#1e1e1e] text-white py-2 px-3 rounded break-words text-[13px] max-w-[85%] mt-1">
                      {msg.text}
                    </div>
                  </div>
                )}

                {msg.sender === 'bot' && (
                 <div className="flex flex-col w-full">
                   <div className="flex items-center gap-3 mb-2">
                    <div className="w-8 h-8 rounded-full bg-black text-white flex items-center justify-center font-bold text-sm">
                      D
                    </div>
                    <div className="flex flex-col">
                      <span className="font-bold text-[13px] text-gray-900 leading-tight">Dodge AI</span>
                      <span className="text-[11px] text-gray-500 font-medium leading-tight">Graph Agent</span>
                    </div>
                   </div>
                   <div className="text-gray-800 text-[14px] mt-1 pr-4">
                     <span dangerouslySetInnerHTML={{ __html: msg.text.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-gray-900">$1</strong>') }} />
                   </div>
                 </div>
                )}
                
              </div>
            ))}

            {loading && (
               <div className="flex flex-col w-full">
                 <div className="flex items-center gap-3 mb-2">
                    <div className="w-8 h-8 rounded-full bg-black text-white flex items-center justify-center font-bold text-sm">
                      D
                    </div>
                    <div className="flex flex-col">
                      <span className="font-bold text-[13px] text-gray-900 leading-tight">Dodge AI</span>
                      <span className="text-[11px] text-gray-500 font-medium leading-tight">Graph Agent</span>
                    </div>
                 </div>
                 <div className="flex gap-1.5 mt-2">
                   <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div>
                   <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                   <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
                 </div>
               </div>
            )}
          </div>

          <div className="p-4 bg-white mt-auto">
            <div className="bg-[#fcfcfc] rounded border border-gray-200 overflow-hidden">
              <div className="flex items-center gap-2 px-3 py-2 bg-[#f4f4f4] border-b border-gray-200">
                <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div>
                <span className="text-[11px] text-gray-700 font-semibold">Dodge AI is awaiting instructions</span>
              </div>
              <div className="flex flex-col pb-2 px-2 bg-white">
                <textarea 
                  className="w-full bg-transparent p-2 outline-none text-[13px] placeholder-gray-500 resize-none mt-1" 
                  placeholder="Analyze anything"
                  rows={2}
                  value={inputVal}
                  onChange={e => setInputVal(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                />
                <div className="flex justify-end pr-1 pt-1">
                  <button 
                    onClick={handleSend} 
                    disabled={loading || !inputVal.trim()}
                    className="px-4 py-1.5 bg-gray-500 text-white text-[13px] font-medium rounded hover:bg-gray-600 disabled:opacity-50 transition-colors"
                  >
                    Send
                  </button>
                </div>
              </div>
            </div>
          </div>
          
        </div>

      </div>
    </div>
  );
};

export default App;
