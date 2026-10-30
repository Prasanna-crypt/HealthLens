import React, { useState } from 'react';
import { Bot, User, Send, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export const AIAssistantPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hello! I am your AI Health Assistant. How can I help you interpret your health data today?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const quickPrompts = [
    "What changed in my latest report?",
    "What should I ask my doctor about?"
  ];

  const handleSend = async (text: string) => {
    if (!text.trim()) return;

    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setInput('');
    setIsLoading(true);

    // Add an empty assistant message — we'll fill it in as chunks arrive
    setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

    const token = localStorage.getItem('healthlens_token');

    try {
      const response = await fetch(`${API_BASE}/api/ai/assistant`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ question: text }),
      });

      if (!response.ok) throw new Error(`Server error: ${response.status}`);

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();

      // Read chunks as they stream in and append to the last message
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        setIsLoading(false); // Hide dots as soon as the first token arrives
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: 'assistant',
            content: updated[updated.length - 1].content + chunk,
          };
          return updated;
        });
      }
    } catch (err: any) {
      const reason = err?.message || 'Unknown error';
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: 'assistant',
          content: `⚠️ Could not reach the AI assistant.\n\n**Reason:** ${reason}\n\nMake sure the backend server is running, then try again.`,
        };
        return updated;
      });
    }

    setIsLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 animate-fade-in flex flex-col h-[calc(100vh-100px)]">
      <div className="mb-4 flex items-center gap-3">
        <div className="bg-primary-100 dark:bg-primary-900/30 p-3 rounded-full">
          <Bot className="w-6 h-6 text-primary-600 dark:text-primary-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">AI Health Assistant</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Ask questions about your medical reports.</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto card p-4 mb-4 flex flex-col gap-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-3 max-w-[80%] ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}>
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-gray-200 dark:bg-gray-700' : 'bg-primary-100 dark:bg-primary-900/30'}`}>
              {msg.role === 'user' ? <User className="w-5 h-5 text-gray-600 dark:text-gray-300" /> : <Bot className="w-5 h-5 text-primary-600 dark:text-primary-400" />}
            </div>
            <div className={`p-4 rounded-2xl ${msg.role === 'user' ? 'bg-primary-600 text-white rounded-tr-sm' : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-tl-sm'}`}>
              <ReactMarkdown
                components={{
                  ul: ({node, ...props}) => <ul className="list-disc ml-5 my-2 space-y-1" {...props} />,
                  ol: ({node, ...props}) => <ol className="list-decimal ml-5 my-2 space-y-1" {...props} />,
                  li: ({node, ...props}) => <li className="leading-relaxed" {...props} />,
                  p: ({node, ...props}) => <p className="mb-2 last:mb-0 leading-relaxed" {...props} />,
                  strong: ({node, ...props}) => <strong className="font-semibold" {...props} />
                }}
              >
                {msg.content}
              </ReactMarkdown>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3 max-w-[80%]">
            <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-primary-100 dark:bg-primary-900/30">
              <Bot className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            </div>
            <div className="p-4 rounded-2xl bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-tl-sm flex items-center gap-1">
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
            </div>
          </div>
        )}
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        {quickPrompts.map(prompt => (
          <button 
            key={prompt} 
            onClick={() => handleSend(prompt)}
            className="flex items-center gap-1 text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 px-3 py-1.5 rounded-full hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-gray-700 dark:text-gray-300"
          >
            <Sparkles className="w-3.5 h-3.5 text-primary-500" /> {prompt}
          </button>
        ))}
      </div>

      <div className="relative">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend(input)}
          placeholder="Ask a health question..."
          className="input-field w-full pr-12 py-4 rounded-full shadow-sm"
        />
        <button 
          onClick={() => handleSend(input)}
          disabled={!input.trim() || isLoading}
          className="absolute right-2 top-2 bottom-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white w-10 flex items-center justify-center rounded-full transition-colors"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
