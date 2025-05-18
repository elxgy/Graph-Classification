import { Box, Button, Container, Grid, Paper, TextField, Typography } from '@mui/material';
import axios from 'axios';
import { useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

interface GraphData {
  nodes: Array<{ id: string }>;
  links: Array<{ source: string; target: string }>;
}

interface AnalysisResult {
  Eulerian: string | string[];
  'Hamiltonian (exact)': string | string[];
  'Hamiltonian (heuristic from 0)': string | string[];
  has_eulerian_cycle: boolean;
  has_eulerian_path: boolean;
  has_hamiltonian_cycle: boolean;
  has_hamiltonian_path: boolean;
  graph_type: string;
  num_vertices: number;
  num_arestas: number;
  time_limit: number;
  max_paths: number;
  exato_time?: number;
  heur_time?: number;
  num_hamiltonian_cycles: number;
  num_hamiltonian_paths: number;
}

function App() {
  const [matrix, setMatrix] = useState<string>('');
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string>('');
  const [selectedPath, setSelectedPath] = useState<number[] | null>(null);
  const [originalGraphData, setOriginalGraphData] = useState<GraphData | null>(null);
  const [startNode, setStartNode] = useState(0);
  const [timeLimit, setTimeLimit] = useState(10);
  const [maxPaths, setMaxPaths] = useState(10000);
  const fgRef = useRef<any>(null);

  const parseMatrix = (matrixStr: string): number[][] => {
    return matrixStr
      .trim()
      .split('\n')
      .map(row => {
        // Remove brackets and commas, then split by whitespace
        const clean = row.replace(/[\[\],]/g, ' ').trim();
        return clean.split(/\s+/).map(Number);
      });
  };

  const createGraphData = (adjMatrix: number[][], highlightPath?: number[]): GraphData => {
    const nodes = adjMatrix.map((_, i) => ({
      id: `Node ${i}`,
      label: `${i}`,
      color: highlightPath && highlightPath.length > 0 && i === highlightPath[0] ? '#00c853' : // nó inicial em verde
        highlightPath?.includes(i) ? '#ff0000' : '#1f77b4'
    }));
    const links: Array<{ source: string; target: string; isPath?: boolean; pathIndex?: number }> = [];

    // Links normais
    for (let i = 0; i < adjMatrix.length; i++) {
      for (let j = 0; j < adjMatrix[i].length; j++) {
        if (adjMatrix[i][j] !== 0) {
          links.push({
            source: `Node ${i}`,
            target: `Node ${j}`
          });
        }
      }
    }

    // Se houver caminho selecionado, adiciona links do caminho com destaque
    if (highlightPath && highlightPath.length > 1) {
      for (let k = 0; k < highlightPath.length - 1; k++) {
        links.push({
          source: `Node ${highlightPath[k]}`,
          target: `Node ${highlightPath[k + 1]}`,
          isPath: true,
          pathIndex: k
        });
      }
    }
    return { nodes, links };
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setMatrix(content);
        try {
          const parsedMatrix = parseMatrix(content);
          const graph = createGraphData(parsedMatrix);
          setGraphData(graph);
          setOriginalGraphData(graph);
          setError('');
          setSelectedPath(null);
        } catch {
          setError('Invalid matrix format in file.');
        }
      };
      reader.readAsText(file);
    }
  };

  const handleMatrixChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMatrix(event.target.value);
    try {
      const parsedMatrix = parseMatrix(event.target.value);
      const graph = createGraphData(parsedMatrix);
      setGraphData(graph);
      setOriginalGraphData(graph);
      setError('');
      setSelectedPath(null);
    } catch {
      setError('Invalid matrix format. Please enter a valid adjacency matrix.');
    }
  };

  const handleAnalyze = async () => {
    try {
      const formData = new FormData();
      const blob = new Blob([matrix], { type: 'text/plain' });
      formData.append('file', blob, 'matrix.txt');
      formData.append('start', String(startNode));
      formData.append('time_limit', String(timeLimit));
      formData.append('max_paths', String(maxPaths));

      const response = await axios.post('http://localhost:5000/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setAnalysisResult(response.data);
      setError('');
      setSelectedPath(null);
    } catch {
      setError('Error analyzing graph. Please check your matrix format.');
    }
  };

  const handlePathClick = (path: string) => {
    const nodes = path.split(' -> ').map(node => parseInt(node));
    const parsedMatrix = parseMatrix(matrix);
    setGraphData(createGraphData(parsedMatrix, nodes));
    setSelectedPath(nodes);
    // Centraliza o grafo no nó inicial
    if (fgRef.current) {
      fgRef.current.centerAt(0, 0, 1000);
    }
  };

  const handleRestoreOriginal = () => {
    if (originalGraphData) {
      setGraphData(originalGraphData);
      setSelectedPath(null);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Analisador de Grafos
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Matriz de Adjacência
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Button variant="contained" component="label">
                ENVIAR ARQUIVO
                <input type="file" hidden accept=".txt" onChange={handleFileUpload} />
              </Button>
            </Box>
            <TextField
              multiline
              rows={6}
              fullWidth
              value={matrix}
              onChange={handleMatrixChange}
              placeholder="Cole ou envie a matriz de adjacência aqui"
              error={!!error}
              helperText={error}
            />
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              <TextField
                label="Vértice inicial"
                type="number"
                value={startNode}
                onChange={e => setStartNode(Number(e.target.value))}
                inputProps={{ min: 0, max: matrix ? parseMatrix(matrix).length - 1 : 0 }}
                size="small"
                sx={{ width: 120 }}
              />
              <TextField
                label="Limite tempo (s)"
                type="number"
                value={timeLimit}
                onChange={e => setTimeLimit(Number(e.target.value))}
                inputProps={{ min: 1, max: 60 }}
                size="small"
                sx={{ width: 120 }}
              />
              <TextField
                label="Máx. caminhos"
                type="number"
                value={maxPaths}
                onChange={e => setMaxPaths(Number(e.target.value))}
                inputProps={{ min: 1, max: 1000000 }}
                size="small"
                sx={{ width: 140 }}
              />
              <Button variant="contained" onClick={handleAnalyze} disabled={!!error}>
                ANALISAR GRAFO
              </Button>
            </Box>
          </Paper>

          {analysisResult && (
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Informações do Grafo
              </Typography>
              <Box sx={{ mb: 2, fontSize: 15 }}>
                <b>Tipo:</b> {analysisResult.graph_type}<br/>
                <b>Número de vértices:</b> {analysisResult.num_vertices}<br/>
                <b>Número de arestas:</b> {analysisResult.num_arestas}<br/>
                <b>Limite de tempo (s):</b> {analysisResult.time_limit}<br/>
                <b>Máx. caminhos:</b> {analysisResult.max_paths}<br/>
                <b>Tempo busca exata:</b> {analysisResult.exato_time?.toFixed(3)}s<br/>
                <b>Tempo busca heurística:</b> {analysisResult.heur_time?.toFixed(3)}s<br/>
                <b>Qtd. ciclos hamiltonianos:</b> {analysisResult.num_hamiltonian_cycles}<br/>
                <b>Qtd. caminhos hamiltonianos:</b> {analysisResult.num_hamiltonian_paths}
              </Box>
              <Typography variant="h6" gutterBottom>
                Resultados
              </Typography>
              {typeof analysisResult["has_eulerian_cycle"] !== 'undefined' && (
                <Typography sx={{ mb: 1 }}>
                  <b>Tem ciclo euleriano?</b> {analysisResult["has_eulerian_cycle"] ? 'Sim' : 'Não'}<br/>
                  <b>Tem caminho euleriano?</b> {analysisResult["has_eulerian_path"] ? 'Sim' : 'Não'}<br/>
                  <b>Tem ciclo hamiltoniano?</b> {analysisResult["has_hamiltonian_cycle"] ? 'Sim' : 'Não'}<br/>
                  <b>Tem caminho hamiltoniano?</b> {analysisResult["has_hamiltonian_path"] ? 'Sim' : 'Não'}
                </Typography>
              )}
              {analysisResult["Eulerian"] && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" fontWeight="bold">
                    Caminho/Ciclo Eureliano:
                  </Typography>
                  <Typography
                    sx={{ cursor: 'pointer', color: 'primary.main', '&:hover': { textDecoration: 'underline' } }}
                    onClick={() => handlePathClick(analysisResult["Eulerian"])}
                  >
                    {analysisResult["Eulerian"]}
                  </Typography>
                </Box>
              )}
              {analysisResult["Hamiltonian cycles"] && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" fontWeight="bold">
                    Ciclos Hamiltonianos:
                  </Typography>
                  {Array.isArray(analysisResult["Hamiltonian cycles"]) ? (
                    analysisResult["Hamiltonian cycles"].map((path: string, idx: number) => (
                      <Typography
                        key={idx}
                        sx={{ 
                          cursor: 'pointer',
                          color: 'primary.main',
                          '&:hover': { textDecoration: 'underline' }
                        }}
                        onClick={() => handlePathClick(path)}
                      >
                        {path}
                      </Typography>
                    ))
                  ) : (
                    <Typography>{analysisResult["Hamiltonian cycles"]}</Typography>
                  )}
                </Box>
              )}
              {analysisResult["Hamiltonian paths"] && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" fontWeight="bold">
                    Caminhos Hamiltonianos:
                  </Typography>
                  {Array.isArray(analysisResult["Hamiltonian paths"]) ? (
                    analysisResult["Hamiltonian paths"].map((path: string, idx: number) => (
                      <Typography
                        key={idx}
                        sx={{ 
                          cursor: 'pointer',
                          color: 'primary.main',
                          '&:hover': { textDecoration: 'underline' }
                        }}
                        onClick={() => handlePathClick(path)}
                      >
                        {path}
                      </Typography>
                    ))
                  ) : (
                    <Typography>{analysisResult["Hamiltonian paths"]}</Typography>
                  )}
                </Box>
              )}
              {Object.entries(analysisResult).map(([key, value]) => (
                key.startsWith("Hamiltonian (heuristic") && (
                  <Box key={key} sx={{ mb: 2 }}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {key.replace('Hamiltonian (heuristic from', 'Hamiltoniano heurístico a partir do vértice').replace(')', '')}:
                    </Typography>
                    {typeof value === 'string' && value.includes('->') ? (
                      <Typography
                        sx={{ cursor: 'pointer', color: 'primary.main', '&:hover': { textDecoration: 'underline' } }}
                        onClick={() => handlePathClick(value)}
                      >
                        {value}
                      </Typography>
                    ) : (
                      <Typography>{value}</Typography>
                    )}
                  </Box>
                )
              ))}
            </Paper>
          )}
        </Grid>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 2, height: '700px' }}>
            <Typography variant="h6" gutterBottom>
              Visualização do Grafo (Direcionado)
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Button variant="outlined" onClick={handleRestoreOriginal} disabled={!originalGraphData}>
                Ver grafo original
              </Button>
            </Box>
            <ForceGraph2D
              ref={fgRef}
              graphData={graphData}
              nodeLabel={node => node.label}
              nodeCanvasObject={(node, ctx, globalScale) => {
                const label = node.label;
                const fontSize = 16/globalScale;
                ctx.beginPath();
                ctx.arc(node.x, node.y, 10, 0, 2 * Math.PI, false);
                ctx.fillStyle = node.color;
                ctx.fill();
                ctx.font = `${fontSize}px Sans-Serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillStyle = '#fff';
                ctx.fillText(label, node.x, node.y);
              }}
              linkDirectionalArrowLength={8}
              linkDirectionalArrowRelPos={1}
              linkColor={link => link.isPath ? '#ffab00' : '#999'}
              linkWidth={link => link.isPath ? 3 : 1}
              nodeColor={node => node.color}
              enableNodeDrag={true}
              width={700}
              height={700}
              linkDistance={220}
              d3Force={(forceType, force) => {
                if (forceType === 'charge') force.strength(-600);
              }}
            />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default App;
