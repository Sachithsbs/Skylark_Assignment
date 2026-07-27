import { useState, useRef, useEffect } from 'react';
import { Send, Trash2, Bot, User, Wrench, AlertTriangle, Sparkles } from 'lucide-react';
import { chat } from '../services/api';
import { ChatMessage } from '../types';

export const ChatInterface = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg: ChatMessage = { role: 'user', content: input.trim() };
    const newHistory = [...messages, userMsg];
    
    setMessages(newHistory);
    setInput('');
    setIsLoading(true);
    setError('');

    try {
      const response = await chat(userMsg.content, messages);
      
      const assistantMsg: ChatMessage & { data_quality_notes?: string[], tool_used?: string | null } = {
        role: 'assistant',
        content: response.reply,
        data_quality_notes: response.data_quality_notes,
        tool_used: response.tool_used
      };
      
      setMessages([...newHistory, assistantMsg]);
    } catch (err: any) {
      setError('Failed to connect to agent. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError('');
  };

  const suggestedQueries = [
    "How is our pipeline looking this quarter?",
    "What's our total accounts receivable?",
    "Show me Renewables sector performance",
    "Which work orders are delayed?",
    "Give me a revenue summary",
    "How's data quality?"
  ];

  const formatMessage = (content: string) => {
    const parts = content.split('\n').map((line, i) => {
      let formattedLine = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      
      if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
        return <li key={i} dangerouslySetInnerHTML={{ __html: formattedLine.substring(2) }} className="ml-4 mb-1 list-disc marker:text-brand-400" />;
      }
      return <p key={i} dangerouslySetInnerHTML={{ __html: formattedLine }} className="mb-2 last:mb-0 min-h-[1em]" />;
    });
    return <div>{parts}</div>;
  };

  return (
    <div className="flex flex-col h-full max-w-5xl mx-auto w-full relative">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto mb-4 rounded-2xl glass-card p-4 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 animate-fade-in">
            <div className="w-20 h-20 rounded-full bg-brand-500/10 flex items-center justify-center mb-6 glow-blue border border-brand-500/20">
              <Sparkles className="w-10 h-10 text-brand-400" />
            </div>
            <h1 className="text-3xl font-bold text-white mb-3">Skylark BI Agent</h1>
            <p className="text-slate-400 max-w-md">
              Ask me anything about your business operations, pipeline, revenue, or data quality using the quick pills below or by typing custom queries.
            </p>
          </div>
        ) : (
          <div className="space-y-6 pb-4">
            {messages.map((msg: any, idx) => (
              <div key={idx} className={`flex w-full message-appear ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex gap-4 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  {/* Avatar */}
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 ${
                    msg.role === 'user' 
                      ? 'bg-gradient-to-tr from-brand-600 to-cyan-500 text-white' 
                      : 'bg-surface-800 border border-brand-500/30 text-brand-400'
                  }`}>
                    {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>

                  {/* Message Bubble */}
                  <div className="flex flex-col gap-2">
                    <div className={`px-5 py-4 rounded-2xl ${
                      msg.role === 'user'
                        ? 'bg-brand-600 text-white rounded-tr-sm shadow-lg shadow-brand-500/20'
                        : 'glass-card text-slate-200 rounded-tl-sm'
                    }`}>
                      {formatMessage(msg.content)}
                    </div>
                    
                    {/* Tool Used Badge */}
                    {msg.tool_used && (
                      <div className="flex items-center gap-1.5 self-start px-2.5 py-1 rounded-md bg-surface-800 border border-white/10 text-xs text-slate-400">
                        <Wrench className="w-3.5 h-3.5 text-cyan-400" />
                        Used: <span className="text-slate-300 font-medium">{msg.tool_used}</span>
                      </div>
                    )}

                    {/* Data Quality Notes */}
                    {msg.data_quality_notes && msg.data_quality_notes.length > 0 && (
                      <div className="flex flex-col gap-1.5 mt-1 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
                        <div className="flex items-center gap-2 text-amber-400 text-xs font-semibold uppercase tracking-wider mb-1">
                          <AlertTriangle className="w-3.5 h-3.5" />
                          Data Quality Notes
                        </div>
                        <ul className="text-sm text-amber-200/80 space-y-1">
                          {msg.data_quality_notes.map((note: string, nIdx: number) => (
                            <li key={nIdx} className="flex items-start gap-2">
                              <span className="text-amber-500 mt-1.5 block w-1 h-1 rounded-full shrink-0" />
                              {note}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            
            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex w-full justify-start message-appear">
                <div className="flex gap-4 max-w-[85%]">
                  <div className="w-8 h-8 rounded-full bg-surface-800 border border-brand-500/30 text-brand-400 flex items-center justify-center shrink-0 mt-1">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="glass-card px-5 py-4 rounded-2xl rounded-tl-sm flex items-center gap-1">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Error Message */}
            {error && (
              <div className="flex justify-center my-4 text-sm text-rose-400 bg-rose-500/10 py-2 px-4 rounded-lg border border-rose-500/20 w-fit mx-auto">
                <AlertTriangle className="w-4 h-4 mr-2 inline" />
                {error}
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Recommended/Suggested Chats Pills (Always Visible above input bar) */}
      <div className="flex flex-wrap items-center gap-2 mb-2 px-2 py-1 select-none animate-slide-up">
        <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold mr-1">Suggestions:</span>
        {suggestedQueries.map((query, i) => (
          <button
            key={i}
            onClick={() => setInput(query)}
            disabled={isLoading}
            className="px-3.5 py-1.5 text-xs font-medium text-slate-300 hover:text-white bg-white/5 hover:bg-brand-500/15 border border-white/10 hover:border-brand-500/30 rounded-full transition-all duration-150 active:scale-95 disabled:opacity-30 disabled:pointer-events-none hover:shadow-[0_0_10px_rgba(59,130,246,0.1)]"
          >
            {query}
          </button>
        ))}
      </div>

      {/* Input Area */}
      <div className="shrink-0 glass-card p-2 rounded-2xl">
        <form onSubmit={handleSubmit} className="relative flex items-end">
          <button
            type="button"
            onClick={clearChat}
            disabled={messages.length === 0 || isLoading}
            className="p-3 m-1 text-slate-500 hover:text-rose-400 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            title="Clear Chat"
          >
            <Trash2 className="w-5 h-5" />
          </button>
          
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about pipeline, revenue, or work orders... (Shift+Enter for new line)"
            className="flex-1 max-h-32 min-h-[52px] bg-transparent text-white placeholder:text-slate-500 p-3 outline-none resize-none overflow-y-auto leading-relaxed"
            rows={1}
            disabled={isLoading}
          />
          
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="p-3 m-1 bg-brand-600 hover:bg-brand-500 text-white rounded-xl transition-all disabled:opacity-50 disabled:bg-surface-800 disabled:text-slate-500 shrink-0 transform hover:-translate-y-0.5 active:translate-y-0"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
      <p className="text-[10px] text-center text-slate-500 mt-2">
        ⚠️ Gemini API (Free Tier) Active. Please use wisely to avoid rate limits. Caching is enabled: identical questions will load from local database memory.
      </p>
    </div>
  );
};
