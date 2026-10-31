const recipes = [
  {
    id: "pudim",
    title: "Pudim de leite",
    description: "Uma sobremesa clássica, assada em banho-maria.",
    image: "/recipes/pudim.svg",
    imageAlt: "Ilustração de um pudim com calda de caramelo em um prato",
    ingredients: [
      "1 xícara de açúcar",
      "1 lata (395 g) de leite condensado",
      "A mesma medida de leite",
      "3 ovos",
    ],
    preparation: [
      "Derreta o açúcar em uma panela até formar um caramelo. Espalhe em uma forma de pudim.",
      "Bata o leite condensado, o leite e os ovos até misturar.",
      "Despeje na forma, cubra com papel-alumínio e asse em banho-maria a 180 °C por cerca de 1 hora e 30 minutos.",
      "Espere esfriar, leve à geladeira por pelo menos 4 horas e desenforme.",
    ],
  },
  {
    id: "pao-de-forno",
    title: "Pão de forno",
    description: "Pão caseiro macio, preparado com ingredientes simples.",
    image: "/recipes/pao-de-forno.svg",
    imageAlt: "Ilustração de um pão caseiro dourado sobre uma tábua",
    ingredients: [
      "500 g de farinha de trigo",
      "10 g de fermento biológico seco",
      "300 ml de água morna",
      "2 colheres de sopa de óleo",
      "1 colher de sopa de açúcar",
      "1 colher de chá de sal",
    ],
    preparation: [
      "Misture a água, o fermento, o açúcar e o óleo. Acrescente a farinha aos poucos e, por último, o sal.",
      "Sove por cerca de 10 minutos, cubra e deixe crescer por 1 hora ou até dobrar de volume.",
      "Modele o pão, coloque em uma forma untada e deixe crescer por mais 30 minutos.",
      "Asse em forno preaquecido a 180 °C por 30 a 35 minutos, até dourar.",
    ],
  },
  {
    id: "frango-assado",
    title: "Frango assado",
    description: "Frango temperado com alho, limão e ervas.",
    image: "/recipes/frango-assado.svg",
    imageAlt: "Ilustração de um frango assado com ervas em uma travessa",
    ingredients: [
      "1 frango inteiro (cerca de 1,5 kg)",
      "2 colheres de sopa de azeite",
      "3 dentes de alho amassados",
      "Suco de 1 limão",
      "Sal, pimenta-do-reino e ervas a gosto",
    ],
    preparation: [
      "Misture o azeite, o alho, o limão, o sal, a pimenta e as ervas. Espalhe o tempero no frango.",
      "Deixe descansar na geladeira por pelo menos 30 minutos.",
      "Coloque em uma assadeira e asse a 200 °C por cerca de 1 hora e 20 minutos, regando com o próprio caldo.",
      "Confira se a parte mais grossa atingiu 74 °C antes de servir. O tempo pode variar conforme o forno e o tamanho da ave.",
    ],
  },
] as const;

export type Recipe = (typeof recipes)[number];

export function getRandomRecipe(excluding?: Recipe["id"]): Recipe {
  const candidates = recipes.filter((recipe) => recipe.id !== excluding);
  return candidates[Math.floor(Math.random() * candidates.length)];
}

export function RecipesPage({ recipe }: { recipe: Recipe }) {
  return (
    <main className="recipes-page">
      <header className="recipes-page__header">
        <p className="recipes-page__eyebrow">Caderno de receitas</p>
        <h1>Receitas para o dia a dia</h1>
        <p>Uma ideia simples para preparar em casa.</p>
      </header>

      <div className="recipes-list">
        <article className="recipe-card" id={recipe.id}>
          <img
            className="recipe-card__image"
            src={recipe.image}
            alt={recipe.imageAlt}
            width="720"
            height="360"
            loading="eager"
            fetchPriority="high"
          />
          <div className="recipe-card__content">
            <h2>{recipe.title}</h2>
            <p className="recipe-card__description">{recipe.description}</p>

            <section aria-labelledby={`${recipe.id}-ingredients`}>
              <h3 id={`${recipe.id}-ingredients`}>Ingredientes</h3>
              <ul>
                {recipe.ingredients.map((ingredient) => (
                  <li key={ingredient}>{ingredient}</li>
                ))}
              </ul>
            </section>

            <section aria-labelledby={`${recipe.id}-preparation`}>
              <h3 id={`${recipe.id}-preparation`}>Modo de preparo</h3>
              <ol>
                {recipe.preparation.map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ol>
            </section>
          </div>
        </article>
      </div>
    </main>
  );
}
