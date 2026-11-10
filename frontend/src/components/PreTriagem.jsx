import React, { useState } from 'react';

export default function PreTriagem() {
  const [formData, setFormData] = useState({
    cpf: '',
    nomeCompleto: '',
    dataNascimento: '',
    idade: '',
    telefone: '',
    email: '',
    queixaPrincipal: '',
    tempoSintomas: '',
    intensidadeDor: 5,
    alergias: '',
    doencasPreexistentes: '',
    medicacoesEmUso: ''
  });

  const [buscandoCPF, setBuscandoCPF] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [carregando, setCarregando] = useState(false);

  const formatarCPF = (valor) => {
    const apenasNumeros = valor.replace(/\D/g, '').slice(0, 11);
    return apenasNumeros
      .replace(/(\d{3})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === 'cpf') {
      const cpfFormatado = formatarCPF(value);
      setFormData((prev) => ({ ...prev, cpf: cpfFormatado }));

      // Ao completar 11 dígitos numéricos, consulta automaticamente a API
      if (cpfFormatado.replace(/\D/g, '').length === 11) {
        consultarCPF(cpfFormatado);
      }
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  // Chama a nova rota /api/v1/triagens/buscar-cpf do FastAPI
  const consultarCPF = async (cpfValor) => {
    setBuscandoCPF(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/triagens/buscar-cpf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cpf: cpfValor.replace(/\D/g, '') })
      });

      if (response.ok) {
        const data = await response.json();
        setFormData((prev) => ({
          ...prev,
          nomeCompleto: data.nome,
          dataNascimento: data.data_nascimento,
          idade: data.idade
        }));
      }
    } catch (err) {
      console.error('Erro ao consultar CPF:', err);
    } finally {
      setBuscandoCPF(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setCarregando(true);

    const payload = {
      paciente: {
        nome_completo: formData.nomeCompleto,
        cpf: formData.cpf.replace(/\D/g, ''),
        data_nascimento: formData.dataNascimento,
        telefone: formData.telefone,
        email: formData.email || null
      },
      queixa_principal: formData.queixaPrincipal,
      tempo_sintomas: formData.tempoSintomas,
      intensidade_dor: parseInt(formData.intensidadeDor, 10),
      historico: {
        alergias: formData.alergias || null,
        doencas_preexistentes: formData.doencasPreexistentes || null,
        medicacoes_em_uso: formData.medicacoesEmUso || null
      }
    };

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/triagens', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const data = await response.json();
        setResultado(data);
      } else {
        alert('Erro ao processar a triagem. Verifique os dados inseridos.');
      }
    } catch (err) {
      console.error(err);
      alert('Não foi possível conectar ao servidor da triagem.');
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 p-6 flex flex-col items-center">
      <header className="w-full max-w-3xl text-center mb-8">
        <h1 className="text-3xl font-bold text-blue-700">MedEasy</h1>
        <p className="text-slate-600 mt-1">Sistema Integrado de Pré-Triagem Hospitalar</p>
      </header>

      <main className="w-full max-w-3xl bg-white shadow-xl rounded-xl p-8 border border-slate-100">
        {!resultado ? (
          <form onSubmit={handleSubmit} className="space-y-6">
            <h2 className="text-xl font-semibold text-slate-700 border-b pb-2">1. Dados do Paciente</h2>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                CPF (Digitação rápida)
              </label>
              <div className="relative">
                <input
                  type="text"
                  name="cpf"
                  required
                  maxLength="14"
                  value={formData.cpf}
                  onChange={handleChange}
                  className="w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="000.000.000-00"
                />
                {buscandoCPF && (
                  <span className="absolute right-3 top-3 text-xs text-blue-600 font-medium animate-pulse">
                    A buscar dados...
                  </span>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-1">Nome Completo</label>
                <input
                  type="text"
                  disabled
                  value={formData.nomeCompleto}
                  className="w-full border border-slate-200 bg-slate-100 font-medium text-slate-700 rounded-lg p-3 cursor-not-allowed"
                  placeholder="Preenchido automaticamente pelo CPF"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Data Nascimento</label>
                <input
                  type="text"
                  disabled
                  value={formData.dataNascimento}
                  className="w-full border border-slate-200 bg-slate-100 font-medium text-slate-700 rounded-lg p-3 cursor-not-allowed"
                  placeholder="AAAA-MM-DD"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Idade Calculada</label>
                <input
                  type="text"
                  disabled
                  value={formData.idade ? `${formData.idade} anos` : ''}
                  className="w-full border border-slate-200 bg-slate-100 font-semibold text-blue-700 rounded-lg p-3 cursor-not-allowed"
                  placeholder="Autocalculado"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Telefone</label>
                <input
                  type="text"
                  name="telefone"
                  required
                  value={formData.telefone}
                  onChange={handleChange}
                  className="w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="(11) 99999-8888"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">E-mail (Opcional)</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="paciente@email.com"
                />
              </div>
            </div>

            <h2 className="text-xl font-semibold text-slate-700 border-b pb-2 pt-4">2. Sintomas e Queixa</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-1">Queixa Principal</label>
                <input
                  type="text"
                  name="queixaPrincipal"
                  required
                  value={formData.queixaPrincipal}
                  onChange={handleChange}
                  className="w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Ex: Dor forte no peito e ansiedade"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Tempo dos sintomas</label>
                <input
                  type="text"
                  name="tempoSintomas"
                  required
                  value={formData.tempoSintomas}
                  onChange={handleChange}
                  className="w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Ex: Há 2 horas"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Intensidade da Dor (0 a 10): <span className="font-bold text-blue-600">{formData.intensidadeDor}</span>
              </label>
              <input
                type="range"
                name="intensidadeDor"
                min="0"
                max="10"
                value={formData.intensidadeDor}
                onChange={handleChange}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
            </div>

            <h2 className="text-xl font-semibold text-slate-700 border-b pb-2 pt-4">3. Histórico Médico</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Alergias</label>
                <input
                  type="text"
                  name="alergias"
                  value={formData.alergias}
                  onChange={handleChange}
                  className="w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Ex: Penicilina"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Doenças Preexistentes</label>
                <input
                  type="text"
                  name="doencasPreexistentes"
                  value={formData.doencasPreexistentes}
                  onChange={handleChange}
                  className="w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Ex: Hipertensão"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Medicações em Uso</label>
                <input
                  type="text"
                  name="medicacoesEmUso"
                  value={formData.medicacoesEmUso}
                  onChange={handleChange}
                  className="w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Ex: Losartana 50mg"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={carregando}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg p-4 transition shadow-md hover:shadow-lg disabled:opacity-50 mt-6"
            >
              {carregando ? 'A enviar Pré-Triagem...' : 'Concluir Pré-Triagem'}
            </button>
          </form>
        ) : (
          <div className="space-y-6 text-center">
            <h2 className="text-2xl font-bold text-slate-800">Pré-Triagem Registada com Sucesso!</h2>
            <div className="p-6 rounded-lg bg-blue-50 border border-blue-200">
              <p className="text-sm font-semibold text-blue-900 uppercase tracking-wider mb-2">Protocolo de Manchester</p>
              <span className={`inline-block text-2xl font-extrabold px-6 py-2 rounded-full text-white shadow-sm ${
                resultado.classificacao_risco === 'VERMELHO' ? 'bg-red-600' :
                resultado.classificacao_risco === 'LARANJA' ? 'bg-orange-500' :
                resultado.classificacao_risco === 'AMARELO' ? 'bg-yellow-500 text-slate-900' :
                'bg-green-600'
              }`}>
                {resultado.classificacao_risco || 'AMARELO'}
              </span>
              <p className="mt-4 text-slate-700"><strong>Paciente:</strong> {resultado.paciente?.nome_completo}</p>
              <p className="text-slate-600"><strong>ID Atendimento:</strong> #{resultado.id}</p>
            </div>
            <button
              onClick={() => setResultado(null)}
              className="w-full bg-slate-200 hover:bg-slate-300 text-slate-800 font-semibold rounded-lg p-3 transition"
            >
              Nova Pré-Triagem
            </button>
          </div>
        )}
      </main>
    </div>
  );
}