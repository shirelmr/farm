import { useState, useEffect } from 'react'

const App = () => {
  const [ducks, setDucks] = useState([]);

  // Inicializar los patos
  useEffect(() => {
    fetch("http://localhost:8000/init", {
      method: 'POST'
    })
    .then(res => res.json())
    .then(res => {
      setDucks(res.ducks);
    });
  }, []);

  // Actualizar las posiciones de los patos
  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://localhost:8000/run")
      .then(res => res.json())
      .then(res => {
        setDucks(res.ducks);
      });
    }, 100); // Actualizar cada 100ms para una animación más fluida

    return () => clearInterval(interval);
  }, []);

  let matrix = [
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0],
  [0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0],
  [0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0],
  [0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0],
  [0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0],
  [0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0],
  [0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0],
  [0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0],
  [0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0],
  [0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0],
  [0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0],
  [0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0],
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
];



  return (
    <div>
      <svg width="800" height="500" xmlns="http://www.w3.org/2000/svg">
      {
        matrix.map((row, rowidx) =>
          row.map((value, colidx) =>
            <rect x={250 + 25 * rowidx} y={5 + 25 * colidx} width={25} height={25} fill={value == 1 ? "lightgray" : "gray"}/>
      ))
      }
      {/* Render all ducks */}
      {ducks.map(duck => (
        <image 
          key={duck.id}
          x={255 + 25 * (duck.pos[0]-1)} 
          y={9 + 25 * (duck.pos[1]-1)} 
          href="ghost.png"
          style={{
            transform: `rotate(${Math.random() * 360}deg)`,
            transformOrigin: 'center'
          }}
        />
      ))}
      </svg>
    </div>
  );

};

export default App;
