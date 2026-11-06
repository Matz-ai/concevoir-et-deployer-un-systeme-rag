import type { Metadata } from "next";

export const metadata: Metadata = { title: "Qualité du modèle — Puls-Events" };
export const dynamic = "force-dynamic"; // les avis et le journal changent à chaque réponse

const API = process.env.PULS_API ?? "http://127.0.0.1:8000";

interface Scores {
  correctes: number;
  questions: number;
  trouves: number;
  attendus: number;
}

interface Qualite {
  total: { v1: Scores; v2: Scores };
  types: { type: string; v1: Scores; v2: Scores }[];
  questions: {
    question: string;
    type: string;
    attendu: string;
    obtenu: string;
    justification: string;
    recherche: string;
    correct_v1: boolean;
    correct_v2: boolean;
  }[];
  avis: { pour: number; contre: number; commentaires: { avis: string; question: string; commentaire: string }[] };
  production: {
    reponses: number;
    euros?: number;
    jetons_entree?: number;
    jetons_sortie?: number;
    recherche_s?: number;
    generation_s?: number;
  };
  donnees: string | null;
}

const nombre = (n: number, chiffres = 0) => n.toLocaleString("fr-FR", { maximumFractionDigits: chiffres });

function Tuile({ titre, valeur, detail }: { titre: string; valeur: string; detail: string }) {
  return (
    <div className="tuile">
      <p className="tuile-titre">{titre}</p>
      <p className="tuile-valeur">{valeur}</p>
      <p className="tuile-detail">{detail}</p>
    </div>
  );
}

function Barre({ version, valeur, sur }: { version: "v1" | "v2"; valeur: number; sur: number }) {
  const texte = `${valeur} / ${sur}`;
  return (
    <div className="barre-ligne" title={`${version.toUpperCase()} : ${texte}`}>
      <span className="barre-version">{version.toUpperCase()}</span>
      <span className="barre-piste">
        <span className={`barre barre--${version}`} style={{ width: `${(valeur / sur) * 100}%` }} />
      </span>
      <span className="barre-valeur">{texte}</span>
    </div>
  );
}

function Verdict({ correct }: { correct: boolean }) {
  return <span className={correct ? "verdict" : "verdict verdict--faux"}>{correct ? "✓ correct" : "✗ incorrect"}</span>;
}

export default async function PageQualite() {
  const reponse = await fetch(`${API}/api/qualite`, { cache: "no-store" }).catch(() => null);
  if (!reponse?.ok) {
    return (
      <main className="page qualite">
        <h1>Qualité du modèle</h1>
        <p className="note note--erreur">L'API Puls-Events ne répond pas. Est-elle lancée ?</p>
      </main>
    );
  }
  const { total, types, questions, avis, production, donnees }: Qualite = await reponse.json();
  const avecRappel = types.filter((t) => t.v2.attendus > 0);
  const votes = avis.pour + avis.contre;

  return (
    <main className="page qualite">
      <h1>Qualité du modèle</h1>
      <p className="qualite-intro">
        Le jeu de test annoté à la main, rejoué au 25/09/2026 sur la V1 (recherche sémantique seule) et la V2 (recherche
        hybride et filtres), puis ce que mesure l'application à chaque question.
        {donnees && ` Données OpenAgenda extraites le ${new Date(donnees).toLocaleDateString("fr-FR")}.`}
      </p>

      <div className="tuiles">
        <Tuile
          titre="Réponses correctes"
          valeur={`${total.v2.correctes} / ${total.v2.questions}`}
          detail={`${total.v1.correctes} / ${total.v1.questions} en V1 · 19 / 22 relu à la main`}
        />
        <Tuile
          titre="Rappel de la recherche"
          valeur={`${total.v2.trouves} / ${total.v2.attendus}`}
          detail={`${total.v1.trouves} / ${total.v1.attendus} en V1`}
        />
        <Tuile
          titre="Coût moyen par question"
          valeur={production.euros === undefined ? "—" : `${nombre(production.euros, 4)} €`}
          detail={production.euros === undefined ? "aucune réponse journalisée" : `sur ${production.reponses} réponse${production.reponses > 1 ? "s" : ""}`}
        />
        <Tuile
          titre="Temps moyen par question"
          valeur={production.recherche_s === undefined ? "—" : `${nombre(production.recherche_s + production.generation_s!, 1)} s`}
          detail={production.recherche_s === undefined ? "aucune réponse journalisée"
            : `recherche ${nombre(production.recherche_s, 1)} s · génération ${nombre(production.generation_s!, 1)} s`}
        />
        <Tuile
          titre="Avis des utilisateurs"
          valeur={votes ? `👍 ${avis.pour} · 👎 ${avis.contre}` : "—"}
          detail={votes ? `${nombre((avis.pour / votes) * 100)} % de réponses jugées utiles` : "aucun avis pour l'instant"}
        />
      </div>

      <h2>Score par type de question</h2>
      <p className="legende">
        <span className="legende-marque barre--v1" aria-hidden="true" /> V1
        <span className="legende-marque barre--v2" aria-hidden="true" /> V2
      </p>
      <div className="groupes">
        {types.map((t) => (
          <div key={t.type}>
            <h3>{t.type}</h3>
            <Barre version="v1" valeur={t.v1.correctes} sur={t.v1.questions} />
            <Barre version="v2" valeur={t.v2.correctes} sur={t.v2.questions} />
          </div>
        ))}
      </div>

      <h2>Rappel de la recherche</h2>
      <p className="qualite-intro">Évènements attendus effectivement retrouvés : c'est ce qui dit si une erreur vient de la recherche ou de la génération.</p>
      <div className="groupes">
        {avecRappel.map((t) => (
          <div key={t.type}>
            <h3>{t.type}</h3>
            <Barre version="v1" valeur={t.v1.trouves} sur={t.v1.attendus} />
            <Barre version="v2" valeur={t.v2.trouves} sur={t.v2.attendus} />
          </div>
        ))}
      </div>

      <h2>Question par question</h2>
      <p className="qualite-intro">
        Verdicts du juge Mistral. Relecture humaine : la météo à Bobigny est un refus correct que le juge trouve trop court.
      </p>
      <div className="questions">
        {questions.map((q) => (
          <details key={q.question}>
            <summary>
              <span className="questions-texte">{q.question}</span>
              <Verdict correct={q.correct_v2} />
            </summary>
            <dl>
              <dt>Type</dt>
              <dd>{q.type}</dd>
              <dt>Attendu</dt>
              <dd>{q.attendu}</dd>
              <dt>Obtenu (V2)</dt>
              <dd className="questions-obtenu">{q.obtenu}</dd>
              <dt>Juge</dt>
              <dd>{q.justification}</dd>
              <dt>Recherche</dt>
              <dd>{q.recherche === "-" ? "aucun évènement attendu" : `${q.recherche} évènements attendus retrouvés`}</dd>
              <dt>En V1</dt>
              <dd><Verdict correct={q.correct_v1} /></dd>
            </dl>
          </details>
        ))}
      </div>

      <h2>En production</h2>
      {production.reponses > 0 ? (
        <table className="production">
          <caption>Moyennes par question, sur le journal de l'application ({production.reponses})</caption>
          <tbody>
            <tr><th scope="row">Jetons d'entrée</th><td>{nombre(production.jetons_entree!)}</td></tr>
            <tr><th scope="row">Jetons de sortie</th><td>{nombre(production.jetons_sortie!)}</td></tr>
            <tr><th scope="row">Coût</th><td>{nombre(production.euros!, 4)} €</td></tr>
            <tr><th scope="row">Lecture des filtres et recherche</th><td>{nombre(production.recherche_s!, 1)} s</td></tr>
            <tr><th scope="row">Génération</th><td>{nombre(production.generation_s!, 1)} s</td></tr>
          </tbody>
        </table>
      ) : (
        <p className="note">Aucune réponse journalisée : posez une question à Puls.</p>
      )}

      <h2>Commentaires des utilisateurs</h2>
      {avis.commentaires.length ? (
        <ul className="commentaires">
          {avis.commentaires.map((c, i) => (
            <li key={i}>
              <span aria-label={c.avis === "pour" ? "Réponse utile" : "Réponse à revoir"}>{c.avis === "pour" ? "👍" : "👎"}</span>{" "}
              {c.commentaire} <span className="commentaires-question">— {c.question}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="note">Aucun commentaire pour l'instant.</p>
      )}
    </main>
  );
}
