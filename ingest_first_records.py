from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from openai import OpenAI
from dotenv import load_dotenv
import os
import time

load_dotenv()

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

oa_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

collection_name = "dharma_qa_seed_en"

records = [
    {"id": 1, "question": "What is Dharma?", "answer": "Dharma is righteous conduct that upholds life, society, and spiritual order."},
    {"id": 2, "question": "What is Aachara?", "answer": "Aachara means prescribed religious conduct, discipline, and purity in daily life."},
    {"id": 3, "question": "What is Upanayanam?", "answer": "Upanayanam is the sacred-thread initiation into Vedic learning and discipline."},

    {"id": 201, "question": "What is Karma Yoga?", "answer": "Karma Yoga is the path of selfless action, where one performs one’s duty without attachment to the fruits of action."},
    {"id": 202, "question": "What is Bhakti Yoga?", "answer": "Bhakti Yoga is the path of devotion and loving surrender to the Lord through prayer, remembrance, and worship."},
    {"id": 203, "question": "What is Jnana Yoga?", "answer": "Jnana Yoga is the path of knowledge and self-inquiry leading to the realization of the true Self."},
    {"id": 204, "question": "What is Dhyana Yoga?", "answer": "Dhyana Yoga is the discipline of meditation that helps steady the mind and direct it toward the Self or the Divine."},
    {"id": 205, "question": "What is Nishkama Karma?", "answer": "Nishkama Karma means performing action without desire for personal gain or attachment to the result."},
    {"id": 206, "question": "What is Karma Phala?", "answer": "Karma Phala refers to the fruits or consequences that arise from one’s actions."},
    {"id": 207, "question": "What is Svadharma?", "answer": "Svadharma is one’s own duty based on role, stage of life, and righteous responsibility."},
    {"id": 208, "question": "What is Samatvam?", "answer": "Samatvam means equanimity, the balanced state of mind in success and failure, pleasure and pain."},
    {"id": 209, "question": "What is Saranagathi?", "answer": "Saranagathi is complete surrender and refuge in the Lord with faith and humility."},
    {"id": 210, "question": "What is Bhakti?", "answer": "Bhakti is devotion, love, and remembrance of the Divine with surrender and trust."},
    {"id": 211, "question": "What is Viveka?", "answer": "Viveka is discrimination between the eternal and the temporary, the real and the unreal."},
    {"id": 212, "question": "What is Vairagya?", "answer": "Vairagya is detachment from worldly cravings and desires while fulfilling one’s duties."},
    {"id": 213, "question": "What is Atman?", "answer": "Atman is the true Self, eternal and beyond the body and mind."},
    {"id": 214, "question": "What is Brahman?", "answer": "Brahman is the supreme absolute reality, infinite and eternal."},
    {"id": 215, "question": "What is Moksha?", "answer": "Moksha is liberation from the cycle of birth and death through realization of the Self."},
    {"id": 216, "question": "What is Sattva?", "answer": "Sattva is the quality of purity, clarity, harmony, and knowledge."},
    {"id": 217, "question": "What is Rajas?", "answer": "Rajas is the quality of activity, desire, restlessness, and passion."},
    {"id": 218, "question": "What is Tamas?", "answer": "Tamas is the quality of inertia, ignorance, laziness, and delusion."},
    {"id": 219, "question": "What is Moha?", "answer": "Moha is delusion or attachment that clouds right judgment."},
    {"id": 220, "question": "What is Krodha?", "answer": "Krodha means anger arising from frustration, attachment, or obstruction of desire."},
    {"id": 221, "question": "What is Lobha?", "answer": "Lobha means greed or excessive desire for possession and gain."},
    {"id": 222, "question": "What is Shraddha?", "answer": "Shraddha is faith, trust, and reverence toward truth, scripture, and the Divine."},
    {"id": 223, "question": "What is Seva?", "answer": "Seva is selfless service offered without expectation of reward."},
    {"id": 224, "question": "What is Tyaga?", "answer": "Tyaga means renunciation of attachment and ego in action."},
    {"id": 225, "question": "What is Prasada Buddhi?", "answer": "Prasada Buddhi is the attitude of accepting all results as the grace of the Lord."},
    {"id": 226, "question": "How to handle stress through Karma Yoga?", "answer": "Handle stress by focusing on performing your duty sincerely without attachment to the result. Offer the action and outcome to the Lord."},
    {"id": 227, "question": "How to overcome anger?", "answer": "Anger can be reduced by self-awareness, patience, controlled speech, and reflecting before reacting."},
    {"id": 228, "question": "How to reduce anxiety about results?", "answer": "Reduce anxiety by concentrating on right effort and accepting results with Prasada Buddhi."},
    {"id": 229, "question": "How to deal with failure?", "answer": "View failure as an opportunity for learning and continue righteous effort without losing balance."},
    {"id": 230, "question": "How to face loss?", "answer": "Face loss with acceptance, prayer, and understanding that all worldly things are temporary."},
    {"id": 231, "question": "How to handle grief?", "answer": "Grief should be handled with prayer, reflection, support from family, and remembrance of the eternal Self."},
    {"id": 232, "question": "How to control the mind?", "answer": "The mind is controlled through discipline, meditation, prayer, and repeated practice."},
    {"id": 233, "question": "How to reduce greed?", "answer": "Reduce greed through contentment, charity, and reflection on impermanence."},
    {"id": 234, "question": "How to practice equanimity?", "answer": "Practice equanimity by remaining balanced in success and failure."},
    {"id": 235, "question": "How to develop devotion?", "answer": "Devotion grows through daily prayer, chanting, remembrance, and surrender to the Divine."},
    {"id": 236, "question": "How to surrender to the Lord?", "answer": "Surrender means offering your fears, desires, and actions to the Lord with trust."},
    {"id": 237, "question": "How to deal with jealousy?", "answer": "Jealousy can be reduced through gratitude and focus on self-improvement."},
    {"id": 238, "question": "How to stay disciplined?", "answer": "Discipline grows through routine, commitment, and control over the senses."},
    {"id": 239, "question": "How to handle family conflict?", "answer": "Family conflict should be approached with patience, truthfulness, and compassion."},
    {"id": 240, "question": "How to balance work and Dharma?", "answer": "Balance work and Dharma by performing professional duties ethically and maintaining daily spiritual discipline."},
    {"id": 241, "question": "How to practice prayer daily?", "answer": "Set aside fixed morning and evening time for prayer and reflection."},
    {"id": 242, "question": "How to improve concentration?", "answer": "Concentration improves through meditation, reduced distractions, and focused effort."},
    {"id": 243, "question": "How to reduce ego?", "answer": "Ego reduces through humility, service, and remembrance that all ability is Divine grace."},
    {"id": 244, "question": "How to remain humble?", "answer": "Humility is maintained through gratitude, service, and respect for others."},
    {"id": 245, "question": "How to live ethically?", "answer": "Live ethically through truthfulness, non-harm, discipline, and fairness."},
    {"id": 246, "question": "How to practice compassion?", "answer": "Compassion is practiced by helping others selflessly and speaking kindly."},
    {"id": 247, "question": "How to control speech?", "answer": "Speech should be truthful, kind, and measured."},
    {"id": 248, "question": "How to develop patience?", "answer": "Patience develops through tolerance, faith, and steady practice."},
    {"id": 249, "question": "How to cultivate inner peace?", "answer": "Inner peace arises from prayer, meditation, detachment, and acceptance."},
    {"id": 250, "question": "How to remain truthful?", "answer": "Truthfulness means aligning thought, word, and action with Dharma."}, 
    {"id": 251, "question": "What is student dharma?", "answer": "Student dharma is disciplined learning, respect for teachers, self-control, and dedication to knowledge and character."},
    {"id": 252, "question": "What is householder dharma?", "answer": "Householder dharma is the righteous fulfillment of duties toward family, society, work, and spiritual life."},
    {"id": 253, "question": "What is husband dharma?", "answer": "Husband dharma includes responsibility, protection, respect, support, and truthful conduct toward the family."},
    {"id": 254, "question": "What is wife dharma?", "answer": "Wife dharma includes care, support, respect, harmony, and righteous partnership in family life."},
    {"id": 255, "question": "What is parent dharma?", "answer": "Parent dharma is nurturing, guiding, protecting, and raising children with values and discipline."},
    {"id": 256, "question": "What is employee dharma?", "answer": "Employee dharma is sincerity, honesty, discipline, respect, and ethical performance of one’s work."},
    {"id": 257, "question": "What is employer dharma?", "answer": "Employer dharma is fairness, compassion, justice, and responsible leadership toward employees."},
    {"id": 258, "question": "What is business dharma?", "answer": "Business dharma is ethical trade, fairness, honesty, and responsibility toward customers and society."},
    {"id": 259, "question": "What is teacher dharma?", "answer": "Teacher dharma is imparting knowledge truthfully, patiently, and with compassion."},
    {"id": 260, "question": "What is priest dharma?", "answer": "Priest dharma is performing rituals correctly, preserving tradition, and guiding devotees spiritually."},
    {"id": 261, "question": "What is ruler dharma?", "answer": "Ruler dharma is just governance, protection of people, and upholding righteousness."},
    {"id": 262, "question": "What is social worker dharma?", "answer": "Social worker dharma is selfless service to society and upliftment of the needy."},
    {"id": 263, "question": "What is soldier dharma?", "answer": "Soldier dharma is courage, discipline, loyalty, and protection of the nation and people."},
    {"id": 264, "question": "What is police dharma?", "answer": "Police dharma is maintaining law, order, justice, and protection of society."},
    {"id": 265, "question": "What is doctor dharma?", "answer": "Doctor dharma is compassionate care, preservation of life, and ethical medical practice."},
    {"id": 266, "question": "What is lawyer dharma?", "answer": "Lawyer dharma is defending justice, truth, and fairness within the law."},
    {"id": 267, "question": "What is judge dharma?", "answer": "Judge dharma is impartial judgment, fairness, and protection of justice."},
    {"id": 268, "question": "What is administrator dharma?", "answer": "Administrator dharma is responsible governance, fairness, and efficient service."},
    {"id": 269, "question": "What is elder dharma?", "answer": "Elder dharma is guidance, wisdom, and support for younger generations."},
    {"id": 270, "question": "What is retiree dharma?", "answer": "Retiree dharma is spiritual reflection, guidance to family, and service to society."},
    {"id": 271, "question": "How should a student live?", "answer": "A student should live with discipline, humility, focused study, and respect for teachers and parents."},
    {"id": 272, "question": "How should a householder live?", "answer": "A householder should live responsibly, ethically, and with balance between family duties and spiritual discipline."},
    {"id": 273, "question": "How should a leader act?", "answer": "A leader should act with integrity, courage, compassion, and justice."},
    {"id": 274, "question": "How should a professional act ethically?", "answer": "A professional should act with honesty, competence, fairness, and accountability."},
    {"id": 275, "question": "How should a devotee live?", "answer": "A devotee should live with devotion, humility, prayer, service, and surrender to the Divine."},
    {"id": 276, "question": "What is duty to parents?", "answer": "Duty to parents is respect, care, gratitude, support, and service throughout life."},
    {"id": 277, "question": "What is duty to children?", "answer": "Duty to children is nurturing, education, guidance, protection, and moral upbringing."},
    {"id": 278, "question": "What is duty to society?", "answer": "Duty to society is ethical conduct, compassion, service, and contribution to collective welfare."},
    {"id": 279, "question": "What is duty to nation?", "answer": "Duty to nation is lawful conduct, service, responsibility, and protection of public good."},
    {"id": 280, "question": "What is duty to the environment?", "answer": "Duty to the environment is preserving nature, avoiding harm, and living responsibly."},
    {"id": 281, "question": "What is charity dharma?", "answer": "Charity dharma is selfless giving to support the needy and uphold righteousness."},
    {"id": 282, "question": "What is dana?", "answer": "Dana means charitable giving with humility and without expectation of return."}, 
    {"id": 283, "question": "What is anna dana?", "answer": "Anna dana is the offering of food to those in need and is considered highly meritorious."},
    {"id": 284, "question": "What is seva to society?", "answer": "Seva to society is selfless service for the welfare of others."},
    {"id": 285, "question": "What is temple dharma?", "answer": "Temple dharma includes reverence, purity, discipline, worship, and service in sacred spaces."},
    {"id": 286, "question": "What is brahmacharya dharma?", "answer": "Brahmacharya dharma is disciplined learning, celibacy, self-control, and focus on knowledge."},
    {"id": 287, "question": "What is grihastha dharma?", "answer": "Grihastha dharma is fulfilling family, social, and professional duties while living ethically."},
    {"id": 288, "question": "What is vanaprastha dharma?", "answer": "Vanaprastha dharma is gradual withdrawal from worldly duties and increased spiritual reflection."},
    {"id": 289, "question": "What is sannyasa dharma?", "answer": "Sannyasa dharma is renunciation, detachment, and complete dedication to spiritual realization."},
    {"id": 290, "question": "What is morning spiritual routine?", "answer": "A morning spiritual routine includes prayer, meditation, gratitude, and setting righteous intention for the day."},
    {"id": 291, "question": "What is evening prayer discipline?", "answer": "Evening prayer discipline includes reflection, gratitude, prayer, and mental calm before rest."},
    {"id": 292, "question": "What is ancestor duty?", "answer": "Ancestor duty includes remembrance, gratitude, and prescribed rites for forefathers."},
    {"id": 293, "question": "What is respect for guru?", "answer": "Respect for guru means humility, service, obedience, and gratitude toward the teacher."},
    {"id": 294, "question": "What is respect for elders?", "answer": "Respect for elders includes reverence, listening, service, and gratitude for their guidance."},
    {"id": 295, "question": "What is duty in crisis?", "answer": "Duty in crisis is to remain calm, act ethically, protect others, and uphold Dharma."},
    {"id": 296, "question": "What is dharma during conflict?", "answer": "Dharma during conflict is truthfulness, justice, restraint, and righteous conduct."},
    {"id": 297, "question": "What is dharma in workplace stress?", "answer": "Dharma in workplace stress is balanced effort, ethical conduct, patience, and detachment from results."},
    {"id": 298, "question": "What is dharma in financial hardship?", "answer": "Dharma in financial hardship is honest effort, discipline, contentment, and faith."},
    {"id": 299, "question": "What is dharma in illness?", "answer": "Dharma in illness is patience, self-care, prayer, and trust in treatment and Divine grace."},
    {"id": 300, "question": "What is dharma in grief?", "answer": "Dharma in grief is acceptance, remembrance of the eternal Self, and support from loved ones."},
    {"id": 301, "question": "What is Karma?", "answer": "Karma is action and the law by which every action produces corresponding results according to Dharma."},
    {"id": 302, "question": "What is Sanatana Dharma?", "answer": "Sanatana Dharma is the timeless, beginningless way of life rooted in the Vedas. It is understood as the eternal order aligned with truth, righteousness, and the natural law that sustains life and spiritual progress."},

    {"id": 303, "question": "Why do religions exist?", "answer": "Religions exist to guide people away from selfish living, establish righteous conduct, and lead them toward God, inner discipline, and lasting well-being beyond temporary pleasures."},

    {"id": 304, "question": "What is Karma?", "answer": "Karma is action and the universal law by which every action, thought, and intention produces corresponding results according to Dharma."},
    {"id": 401, "question": "Why should one follow Dharma?", "answer": "One should follow Dharma because Dharma protects the individual and society, disciplines life, and leads one toward higher good and spiritual well-being."}

]

def make_point(record: dict) -> PointStruct:
    text = f"Q: {record['question']}\nA: {record['answer']}"
    embedding = oa_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding

    return PointStruct(
        id=record["id"],
        vector=embedding,
        payload={
    "question": record["question"],
    "answer": record["answer"],
    "evidence": record.get("evidence"),
    "source_basis": "Dharma seed Q&A",
    "qualification": "General foundational definition."
}
    )

points = [make_point(r) for r in records]

batch_size = 5
for i in range(0, len(points), batch_size):
    batch = points[i:i + batch_size]
    qdrant.upsert(
        collection_name=collection_name,
        points=batch,
        wait=True,
    )
    print(f"Uploaded batch {i // batch_size + 1}: {len(batch)} record(s)")
    time.sleep(1)

print("Ingestion completed successfully.")
