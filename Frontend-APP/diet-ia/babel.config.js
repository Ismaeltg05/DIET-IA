module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['expo'],
    plugins: [
  ['nativewind/babel'], // Comentar para funcionar  sin Tailwind
  ],
  };
};