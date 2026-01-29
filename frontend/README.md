# TestSuiteGen Frontend

![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=next.js&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-DB-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Monaco Editor](https://img.shields.io/badge/Monaco_Editor-IDE-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white)

The user interface for TestSuiteGen, providing a modern, real-time dashboard for automated test generation. Features include live log streaming, interactive configuration, and a built-in code editor.

## Setup & Installation

1.  **Navigate to the frontend directory:**

    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    # or
    yarn install
    ```

## Running the Application

### Development Mode

Start the development server with hot-reloading:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`.

### Production Build

Create an optimized production build:

```bash
npm run build
npm run start
```

## Project Structure

```text
frontend/
├── app/                        # Next.js 16 App Router
│   ├── api/                    # Route handlers (if any)
│   ├── globals.css             # Tailwind 4 global styles
│   ├── layout.tsx              # Root layout & providers
│   └── page.tsx                # Main Dashboard implementation
├── components/                 # React Components
│   ├── ui/                     # Base UI primitives (Buttons, Inputs, etc.)
│   ├── ArtifactsTabs.tsx       # Manages generated test files
│   ├── ConfigPanel.tsx         # LLM & Job configuration
│   ├── EditorPanel.tsx         # Monaco-based code editor
│   ├── EndpointsWidget.tsx     # API endpoint discovery/selection
│   ├── Header.tsx              # Site navigation & logo
│   ├── IntentSelector.tsx      # Test case intent prioritization
│   ├── LogViewer.tsx           # Real-time backend logs
│   ├── PipelineStatus.tsx      # Visual generation progress
│   ├── ResultsPanel.tsx        # Success/Failure summaries
│   └── SessionsSidebar.tsx     # History & navigation
├── lib/                        # Logic & Utilities
│   ├── api.ts                  # Backend service client
│   ├── supabase.ts             # Supabase client instantiation
│   └── utils.ts                # Formatting & UI helpers
├── public/                     # Static assets (images, icons)
├── package.json                # Dependencies & Scripts
├── next.config.ts              # Next.js configuration
└── tsconfig.json               # TypeScript configuration
```

## Environment Variables

Create a `.env.local` file in the `frontend` directory:

| Variable                        | Description                | Example                   |
| :------------------------------ | :------------------------- | :------------------------ |
| `NEXT_PUBLIC_BACKEND_URL`       | URL of the FastAPI backend | `http://localhost:8000`   |
| `NEXT_PUBLIC_SUPABASE_URL`      | Your Supabase Project URL  | `https://xyz.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase Public Anon Key   | `eyJ...`                  |

## Features

- **Real-time Updates**: Visual progress tracking via pipeline cards.
- **Code Preview**: Built-in Monaco editor for viewing generated tests.
- **Dynamic Config**: Switch between Gemini, Groq, and local LLMs on the fly.
- **Artifact Management**: Batch download generated test suites as `.zip`.
