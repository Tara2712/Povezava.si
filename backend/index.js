const express = require('express');
require('dotenv').config();

const app = express();
app.use(express.json());

app.get('/', (req, res) => {
  res.json({ sporocilo: 'Backend deluje!' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Strežnik teče na portu ${PORT}`));