import { useRef, useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

// Cores e rótulos da classificação (a API devolve sempre em MAIÚSCULAS)
const RISCO = {
  VERMELHO: { rotulo: 'Emergência', classe: 'bg-red-600 text-white' },
  LARANJA: { rotulo: 'Muito urgente', classe: 'bg-orange-500 text-white' },
  AMARELO: { rotulo: 'Urgente', classe: 'bg-yellow-400 text-slate-900' },
  VERDE: { rotulo: 'Pouco urgente', classe: 'bg-green-600 text-white' },
  AZUL: { rotulo: 'Não urgente', classe: 'bg-blue-600 text-white' },
};

const ESTADO_INICIAL = {
  cpf: '',
  nomeCompleto: '',
  dataNascimento: '',
  telefone: '',
  email: '',
  queixaPrincipal: '',
  tempoSintomas: '',
  intensidadeDor: 5,
  pressaoArterial: '',
  frequenciaCardiaca: '',
  temperatura: '',
  saturacao: '',
  alergias: '',
  doencasPreexistentes: '',
  medicacoesEmUso: '',
};

const inputClasse =
  'w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none';

const formatarCPF = (valor) => {
  const apenasNumeros = valor.replace(/\D/g, '').slice(0, 11);
  return apenasNumeros
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
};

const formatarTelefone = (valor) => {
  const d = valor.replace(/\D/g, '').slice(0, 11);
  if (d.length === 0) return '';
  if (d.length <= 2) return `(${d}`;
  if (d.length <= 6) return `(${d.slice(0, 2)}) ${d.slice(2)}`;
  if (d.length <= 10) return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`;
  return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`;
};

const calcularIdade = (dataIso) => {
  if (!dataIso) return '';
  const nasc = new Date(`${dataIso}T00:00:00`);
  if (Number.isNaN(nasc.getTime())) return '';
  const hoje = new Date();
  let idade = hoje.getFullYear() - nasc.getFullYear();
  const aindaNaoFez =
    hoje.getMonth() < nasc.getMonth() ||
    (hoje.getMonth() === nasc.getMonth() && hoje.getDate() < nasc.getDate());
  if (aindaNaoFez) idade -= 1;
  return idade >= 0 ? idade : '';
};

// Transforma o corpo de erro da API (FastAPI) em mensagens legíveis
const mensagensDeErro = async (response) => {
  try {
    const corpo = await response.json();
    if (Array.isArray(corpo.detail)) {
      return corpo.detail.map((e) => {
        const campo = e.loc?.[e.loc.length - 1];
        const texto = String(e.msg ?? '').replace(/^Value error, /, '');
        return campo ? `${campo}: ${texto}` : texto;
      });
    }
    if (typeof corpo.detail === 'string') return [corpo.detail];
  } catch {
    // corpo sem JSON: cai na mensagem padrão abaixo
  }
  return ['Erro ao processar a triagem. Verifique os dados inseridos.'];
};

function Campo({ id, rotulo, className = '', children }) {
  return (
    <div className={className}>
      <label htmlFor={id} className="block text-sm font-medium text-slate-700 mb-1">
        {rotulo}
      </label>
      {children}
    </div>
  );
}

export default function PreTriagem() {
  const [formData, setFormData] = useState(ESTADO_INICIAL);
  const [buscandoCPF, setBuscandoCPF] = useState(false);
  const [avisoCPF, setAvisoCPF] = useState(null); // { tipo: 'ok' | 'erro', texto }
  const [erros, setErros] = useState([]);
  const [resultado, setResultado] = useState(null);
  const [carregando, setCarregando] = useState(false);
  const ultimaBusca = useRef(0); // descarta respostas antigas da consulta de CPF

  const idade = calcularIdade(formData.dataNascimento);
  const hojeIso = new Date().toISOString().slice(0, 10);

  const atualizar = (campo, valor) =>
    setFormData((prev) => ({ ...prev, [campo]: valor }));

  const consultarCPF = async (cpfDigitos) => {
    const numeroDaBusca = ++ultimaBusca.current;
    setBuscandoCPF(true);
    setAvisoCPF(null);
    try {
      const response = await fetch(`${API_URL}/api/v1/triagens/buscar-cpf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cpf: cpfDigitos }),
      });
      if (numeroDaBusca !== ultimaBusca.current) return;

      if (response.ok) {
        const data = await response.json();
        setFormData((prev) => ({
          ...prev,
          nomeCompleto: data.nome,
          dataNascimento: data.data_nascimento,
        }));
        setAvisoCPF({ tipo: 'ok', texto: 'Dados encontrados (base simulada). Confira antes de continuar.' });
      } else {
        const [mensagem] = await mensagensDeErro(response);
        setAvisoCPF({ tipo: 'erro', texto: mensagem });
      }
    } catch (err) {
      if (numeroDaBusca !== ultimaBusca.current) return;
      console.error('Erro ao consultar CPF:', err);
      setAvisoCPF({
        tipo: 'erro',
        texto: 'Não foi possível consultar o CPF. Preencha os dados manualmente.',
      });
    } finally {
      if (numeroDaBusca === ultimaBusca.current) setBuscandoCPF(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    if (name === 'cpf') {
      const cpfFormatado = formatarCPF(value);
      atualizar('cpf', cpfFormatado);
      const digitos = cpfFormatado.replace(/\D/g, '');
      if (digitos.length === 11) {
        consultarCPF(digitos); // consulta ao completar 11 dígitos
      } else {
        ultimaBusca.current++; // cancela busca pendente
        setBuscandoCPF(false);
        setAvisoCPF(null);
      }
    } else if (name === 'telefone') {
      atualizar('telefone', formatarTelefone(value));
    } else {
      atualizar(name, value);
    }
  };

  const montarPayload = () => {
    const sinais = {};
    if (formData.pressaoArterial.trim()) sinais.pressao_arterial = formData.pressaoArterial.trim();
    if (formData.frequenciaCardiaca !== '') sinais.frequencia_cardiaca = parseInt(formData.frequenciaCardiaca, 10);
    if (formData.temperatura.trim() !== '') sinais.temperatura = parseFloat(formData.temperatura.replace(',', '.'));
    if (formData.saturacao !== '') sinais.saturacao_oxigenio = parseInt(formData.saturacao, 10);

    return {
      paciente: {
        nome_completo: formData.nomeCompleto.trim(),
        cpf: formData.cpf.replace(/\D/g, ''),
        data_nascimento: formData.dataNascimento,
        telefone: formData.telefone.replace(/\D/g, ''),
        email: formData.email.trim() || null,
      },
      queixa_principal: formData.queixaPrincipal.trim(),
      tempo_sintomas: formData.tempoSintomas.trim(),
      intensidade_dor: parseInt(formData.intensidadeDor, 10),
      historico: {
        alergias: formData.alergias.trim() || null,
        doencas_preexistentes: formData.doencasPreexistentes.trim() || null,
        medicacoes_em_uso: formData.medicacoesEmUso.trim() || null,
      },
      sinais_vitais: sinais,
    };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErros([]);
    setCarregando(true);

    try {
      const response = await fetch(`${API_URL}/api/v1/triagens`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(montarPayload()),
      });

      if (response.ok) {
        setResultado(await response.json());
      } else {
        setErros(await mensagensDeErro(response));
      }
    } catch (err) {
      console.error(err);
      setErros(['Não foi possível conectar ao servidor da triagem.']);
    } finally {
      setCarregando(false);
    }
  };

  const novaTriagem = () => {
    ultimaBusca.current++;
    setFormData(ESTADO_INICIAL);
    setAvisoCPF(null);
    setErros([]);
    setResultado(null);
  };

  const risco = resultado ? RISCO[resultado.classificacao_risco] : null;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 p-6 flex flex-col items-center">
      <header className="w-full max-w-3xl text-center mb-6">
        <h1 className="text-3xl font-bold text-blue-700">MedEasy</h1>
        <p className="text-slate-600 mt-1">Sistema Integrado de Pré-Triagem Hospitalar</p>
      </header>

      <div
        role="note"
        className="w-full max-w-3xl mb-6 rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900"
      >
        <strong>Projeto acadêmico.</strong> Use apenas dados fictícios. A classificação é
        simplificada e não substitui a avaliação de um profissional de saúde. Em caso de
        emergência, ligue <strong>192 (SAMU)</strong>.
      </div>

      <main className="w-full max-w-3xl bg-white shadow-xl rounded-xl p-8 border border-slate-100">
        {!resultado ? (
          <form onSubmit={handleSubmit} className="space-y-6">
            <h2 className="text-xl font-semibold text-slate-700 border-b pb-2">1. Dados do Paciente</h2>

            <Campo id="cpf" rotulo="CPF">
              <div className="relative">
                <input
                  id="cpf"
                  type="text"
                  name="cpf"
                  required
                  inputMode="numeric"
                  maxLength={14}
                  value={formData.cpf}
                  onChange={handleChange}
                  className={inputClasse}
                  placeholder="000.000.000-00"
                  aria-describedby="aviso-cpf"
                />
                {buscandoCPF && (
                  <span className="absolute right-3 top-3 text-xs text-blue-600 font-medium animate-pulse">
                    Buscando dados...
                  </span>
                )}
              </div>
              <p
                id="aviso-cpf"
                role="status"
                className={`mt-1 text-xs ${avisoCPF?.tipo === 'erro' ? 'text-red-600' : 'text-green-700'}`}
              >
                {avisoCPF?.texto}
              </p>
            </Campo>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Campo id="nomeCompleto" rotulo="Nome completo" className="md:col-span-2">
                <input
                  id="nomeCompleto"
                  type="text"
                  name="nomeCompleto"
                  required
                  minLength={3}
                  value={formData.nomeCompleto}
                  onChange={handleChange}
                  className={inputClasse}
                  placeholder="Preenchido pelo CPF ou digite"
                />
              </Campo>

              <Campo id="dataNascimento" rotulo="Data de nascimento">
                <input
                  id="dataNascimento"
                  type="date"
                  name="dataNascimento"
                  required
                  max={hojeIso}
                  value={formData.dataNascimento}
                  onChange={handleChange}
                  className={inputClasse}
                />
              </Campo>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Campo id="idade" rotulo="Idade calculada">
                <input
                  id="idade"
                  type="text"
                  readOnly
                  value={idade !== '' ? `${idade} anos` : ''}
                  className="w-full border border-slate-200 bg-slate-100 font-semibold text-blue-700 rounded-lg p-3"
                  placeholder="Automático"
                />
              </Campo>

              <Campo id="telefone" rotulo="Telefone">
                <input
                  id="telefone"
                  type="tel"
                  name="telefone"
                  required
                  value={formData.telefone}
                  onChange={handleChange}
                  className={inputClasse}
                  placeholder="(11) 99999-8888"
                />
              </Campo>

              <Campo id="email" rotulo="E-mail (opcional)">
                <input
                  id="email"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className={inputClasse}
                  placeholder="paciente@email.com"
                />
              </Campo>
            </div>

            <h2 className="text-xl font-semibold text-slate-700 border-b pb-2 pt-4">2. Sintomas e Queixa</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Campo id="queixaPrincipal" rotulo="Queixa principal" className="md:col-span-2">
                <input
                  id="queixaPrincipal"
                  type="text"
                  name="queixaPrincipal"
                  required
                  minLength={5}
                  value={formData.queixaPrincipal}
                  onChange={handleChange}
                  className={inputClasse}
                  placeholder="Ex: Dor forte no peito e ansiedade"
                />
              </Campo>

              <Campo id="tempoSintomas" rotulo="Tempo dos sintomas">
                <input
                  id="tempoSintomas"
                  type="text"
                  name="tempoSintomas"
                  required
                  value={formData.tempoSintomas}
                  onChange={handleChange}
                  className={inputClasse}
                  placeholder="Ex: Há 2 horas"
                />
              </Campo>
            </div>

            <div>
              <label htmlFor="intensidadeDor" className="block text-sm font-medium text-slate-700 mb-1">
                Intensidade da dor (0 a 10):{' '}
                <span className="font-bold text-blue-600">{formData.intensidadeDor}</span>
              </label>
              <input
                id="intensidadeDor"
                type="range"
                name="intensidadeDor"
                min="0"
                max="10"
                value={formData.intensidadeDor}
                onChange={handleChange}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
            </div>

            <h2 className="text-xl font-semibold text-slate-700 border-b pb-2 pt-4">
              3. Sinais Vitais <span className="text-sm font-normal text-slate-500">(opcional)</span>
            </h2>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Campo id="pressaoArterial" rotulo="Pressão (mmHg)">
                <input
                  id="pressaoArterial"
                  type="text"
                  name="pressaoArterial"
                  inputMode="numeric"
                  pattern="\d{2,3}/\d{2,3}"
                  title="Use o formato 120/80"
                  value={formData.pressaoArterial}
                  onChange={handleChange}
                  className={inputClasse}
                  placeholder="120/80"
                />
              </Campo>

              <Campo id="frequenciaCardiaca" rotulo="Freq. cardíaca (bpm)">
                <input
                  id="frequenciaCardiaca"
                  type="number"
                  name="frequenciaCardiaca"
                  min="30"
                  max="250"
                  value={formData.frequenciaCardiaca}
                  onChange={handleChange}
                  className={inputClasse}
                  placeholder="75"
                />
              </Campo>

              <Campo id="temperatura" rotulo="Temperatura (°C)">
                <input
                  id="temperatura"
                  type="text"
                  name="temperatura"
                  inputMode="decimal"
                  pattern="[0-9]+([.,][0-9]+)?"
                  title="Ex.: 36,5"
                  value={formData.temperatura}
                  onChange={handleChange}
                  className={inputClasse}
                  placeholder="36,5"
                />
              </Campo>

              <Campo id="saturacao" rotulo="Saturação O₂ (%)">
                <input
                  id="saturacao"
                  type="number"
                  name="saturacao"
                  min="0"
                  max="100"
                  value={formData.saturacao}
                  onChange={handleChange}
                  className={inputClasse}
                  placeholder="98"
                />
              </Campo>
            </div>

            <h2 className="text-xl font-semibold text-slate-700 border-b pb-2 pt-4">4. Histórico Médico</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Campo id="alergias" rotulo="Alergias">
                <input
                  id="alergias"
                  type="text"
                  name="alergias"
                  value={formData.alergias}
                  onChange={handleChange}
                  className={inputClasse}
                  placeholder="Ex: Penicilina"
                />
              </Campo>

              <Campo id="doencasPreexistentes" rotulo="Doenças preexistentes">
                <input
                  id="doencasPreexistentes"
                  type="text"
                  name="doencasPreexistentes"
                  value={formData.doencasPreexistentes}
                  onChange={handleChange}
                  className={inputClasse}
                  placeholder="Ex: Hipertensão"
                />
              </Campo>

              <Campo id="medicacoesEmUso" rotulo="Medicações em uso">
                <input
                  id="medicacoesEmUso"
                  type="text"
                  name="medicacoesEmUso"
                  value={formData.medicacoesEmUso}
                  onChange={handleChange}
                  className={inputClasse}
                  placeholder="Ex: Losartana 50mg"
                />
              </Campo>
            </div>

            {erros.length > 0 && (
              <div role="alert" className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-800">
                <p className="font-semibold mb-1">Não foi possível concluir:</p>
                <ul className="list-disc pl-5 space-y-0.5">
                  {erros.map((mensagem) => (
                    <li key={mensagem}>{mensagem}</li>
                  ))}
                </ul>
              </div>
            )}

            <button
              type="submit"
              disabled={carregando}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg p-4 transition shadow-md hover:shadow-lg disabled:opacity-50 mt-6"
            >
              {carregando ? 'Enviando pré-triagem...' : 'Concluir pré-triagem'}
            </button>
          </form>
        ) : (
          <div className="space-y-6 text-center">
            <h2 className="text-2xl font-bold text-slate-800">Pré-triagem registrada com sucesso!</h2>

            <div className="p-6 rounded-lg bg-blue-50 border border-blue-200">
              <p className="text-sm font-semibold text-blue-900 mb-2">
                Classificação de risco (simplificada)
              </p>

              {risco ? (
                <>
                  <span className={`inline-block text-2xl font-extrabold px-6 py-2 rounded-full shadow-sm ${risco.classe}`}>
                    {resultado.classificacao_risco}
                  </span>
                  <p className="mt-2 text-slate-700">{risco.rotulo}</p>
                </>
              ) : (
                <span className="inline-block text-lg font-semibold px-6 py-2 rounded-full bg-slate-200 text-slate-700">
                  Classificação indisponível
                </span>
              )}

              <p className="mt-4 text-slate-700">
                <strong>Paciente:</strong> {resultado.paciente?.nome_completo}
              </p>
              <p className="text-slate-600">
                <strong>ID do atendimento:</strong> #{resultado.id}
              </p>
            </div>

            <p className="text-xs text-slate-500">
              Esta classificação não substitui a avaliação de um profissional de saúde.
            </p>

            <button
              onClick={novaTriagem}
              className="w-full bg-slate-200 hover:bg-slate-300 text-slate-800 font-semibold rounded-lg p-3 transition"
            >
              Nova pré-triagem
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
