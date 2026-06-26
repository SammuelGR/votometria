# Frontend Votometria

Frontend React do Votometria.

Stack principal:

- Vite
- React
- TypeScript
- Tailwind CSS
- React Router
- TanStack Query
- Recharts

## Requisitos

- Node 24 LTS recomendado
- Node 22.12 ou superior suportado pelo Vite 8

## Configuração

Crie uma cópia do arquivo `.env.example` dentro de `/frontend` e renomeie-a para `.env`.

Preencha `VITE_API_BASE_URL` com a URL base da API backend, incluindo o prefixo `/api`.

## Instalação

```bash
npm install
```

## Desenvolvimento

```bash
npm run dev
```

## Validação

```bash
npm run format:check
npm run lint
npm run build
```

## Estrutura

- `src/App.tsx`: providers globais.
- `src/config`: configuração de ambiente do frontend.
- `src/routes`: rotas e paths centralizados.
- `src/pages`: páginas organizadas por contexto.
- `src/components/ui`: componentes visuais compartilhados.
- `src/fetchers`: funções de acesso à API e hooks de TanStack Query.
- `src/models`: modelos de domínio compartilhados no frontend.
- `src/utils`: utilitários compartilhados.
