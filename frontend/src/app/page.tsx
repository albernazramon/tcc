'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, Database, Code, Lightbulb } from 'lucide-react';

interface OptimizeResponse {
  optimized_query: string;
  original_query: string;
  insights: string;
}

export default function Home() {
  const [query, setQuery] = useState('');
  const [schema, setSchema] = useState('');
  const [additionalInfo, setAdditionalInfo] = useState('');
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [result, setResult] = useState<OptimizeResponse | null>(null);
  const { toast } = useToast();

  const handleOptimize = async () => {
    if (!query.trim() || !schema.trim()) return;

    setIsOptimizing(true);
    setResult(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      const res = await fetch(`${apiUrl}/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          schema,
          additional_info: additionalInfo,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Erro ao otimizar a consulta.');
      }

      const data = await res.json();
      setResult(data);

      toast({
        title: 'Sucesso!',
        description: 'A consulta foi otimizada com sucesso.',
        variant: 'default',
      });
    } catch (error: unknown) {
      console.error('Erro ao otimizar consulta:', error);
      const errMessage =
        error instanceof Error
          ? error.message
          : 'Erro inesperado. Verifique o console.';
      toast({
        title: 'Erro ao otimizar consulta',
        description: errMessage,
        variant: 'destructive',
      });
    } finally {
      setIsOptimizing(false);
    }
  };

  return (
    <main className='min-h-screen bg-gray-50 p-4 md:p-8 font-sans text-gray-800 flex flex-col'>
      <div className='max-w-[95%] mx-auto w-full flex-1 flex flex-col space-y-6'>
        <header className='text-center py-6'>
          <h1 className='text-4xl font-bold text-blue-700 flex items-center justify-center gap-2'>
            <Database className='w-10 h-10' /> SQL Optimizer
          </h1>
          <p className='text-gray-500 mt-2 text-lg'>
            Otimize suas consultas PostgreSQL
          </p>
        </header>

        <div className='grid grid-cols-1 lg:grid-cols-2 gap-8 flex-1'>
          <div className='bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col space-y-5 h-[700px] sticky top-8'>
            <div className='flex-1 flex flex-col'>
              <label className='block text-base font-semibold text-gray-700 mb-2 flex items-center gap-2'>
                <Code className='w-5 h-5 text-blue-500' /> Consulta SQL Original
              </label>
              <Textarea
                value={query}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                  setQuery(e.target.value)
                }
                placeholder='SELECT * FROM users WHERE...'
                className='h-full w-full p-4 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none font-mono'
              />
            </div>

            <div className='flex-1 flex flex-col'>
              <label className='block text-base font-semibold text-gray-700 mb-2 flex items-center gap-2'>
                <Database className='w-5 h-5 text-blue-500' /> Estrutura do
                Banco (DDL / Schemas)
              </label>
              <Textarea
                value={schema}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                  setSchema(e.target.value)
                }
                placeholder='CREATE TABLE users (id INT, name VARCHAR(50));...'
                className='h-full w-full p-4 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none font-mono'
              />
            </div>

            <div className='flex flex-col'>
              <label className='block text-base font-semibold text-gray-700 mb-2 flex items-center gap-2'>
                <Lightbulb className='w-5 h-5 text-blue-500' /> Informações
                Adicionais (Opcional)
              </label>
              <Textarea
                value={additionalInfo}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                  setAdditionalInfo(e.target.value)
                }
                placeholder='Qualquer contexto extra, índice existente ou objetivo específico...'
                className='h-24 w-full p-4 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none font-sans'
              />
            </div>

            <Button
              onClick={handleOptimize}
              disabled={isOptimizing || !query.trim() || !schema.trim()}
              className='w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-6 px-4 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed text-lg'
            >
              {isOptimizing ? (
                <>
                  <Loader2 className='w-6 h-6 animate-spin' /> Otimizando
                  Consulta...
                </>
              ) : (
                <>
                  <Lightbulb className='w-6 h-6' /> Otimizar Consulta
                </>
              )}
            </Button>
          </div>

          <div className='bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col min-h-[700px] h-full'>
            {result ? (
              <div className='flex-1 overflow-y-auto p-8 space-y-8'>
                <div>
                  <h3 className='text-lg font-semibold text-gray-700 mb-3 flex items-center gap-2'>
                    <Code className='w-6 h-6 text-green-500' /> Consulta
                    Otimizada
                  </h3>
                  <div className='bg-gray-50 p-5 rounded-xl border border-gray-200 font-mono text-[15px] overflow-x-auto whitespace-pre-wrap leading-relaxed'>
                    {result.optimized_query ||
                      'Nenhuma consulta retornada (Verifique os insights abaixo)'}
                  </div>
                </div>

                <div>
                  <h3 className='text-lg font-semibold text-gray-700 mb-3 flex items-center gap-2'>
                    <Lightbulb className='w-6 h-6 text-yellow-500' /> Insights e
                    Análises
                  </h3>
                  <div className='prose prose-base max-w-none text-gray-700 bg-blue-50/30 p-6 rounded-xl border border-blue-100/50'>
                    <ReactMarkdown>{result.insights}</ReactMarkdown>
                  </div>
                </div>
              </div>
            ) : (
              <div className='flex-1 flex flex-col items-center justify-center text-gray-400 p-10 text-center space-y-6'>
                <div className='p-6 bg-gray-50 rounded-full'>
                  <Database className='w-20 h-20 text-gray-300' />
                </div>
                <div className='space-y-2'>
                  <h3 className='text-xl font-medium text-gray-500'>
                    Nenhuma otimização realizada
                  </h3>
                  <p className='max-w-md mx-auto text-gray-400'>
                    Preencha a consulta SQL original e o schema das tabelas ao
                    lado e clique em otimizar para obter sugestões de
                    desempenho, criação de índices e muito mais.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
