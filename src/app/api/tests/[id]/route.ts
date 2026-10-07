import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    success: true,
    data: {
      test: {
        id: "demo-test-001",
        title: "UPSC Prelims Mock Test - Demo",
        totalQuestions: 10,
        durationMinutes: 20,
        subjects: ["Polity", "Economy", "Geography"],
      },
      questions: [
        { id: "q1", number: 1, text: "Under which Article has the Supreme Court placed the Right to Privacy?", options: [{ id: "a", text: "Article 15" }, { id: "b", text: "Article 16" }, { id: "c", text: "Article 19" }, { id: "d", text: "Article 21" }] },
        { id: "q2", number: 2, text: "A Money Bill under Article 110 can be introduced in:", options: [{ id: "a", text: "Lok Sabha only" }, { id: "b", text: "Rajya Sabha only" }, { id: "c", text: "Either House" }, { id: "d", text: "Joint Session" }] },
        { id: "q3", number: 3, text: "The Ring of Fire is associated with:", options: [{ id: "a", text: "Atlantic Ocean" }, { id: "b", text: "Pacific Ocean" }, { id: "c", text: "Indian Ocean" }, { id: "d", text: "Arctic Ocean" }] },
        { id: "q4", number: 4, text: "CRISPR-Cas9 technology is primarily used for:", options: [{ id: "a", text: "Cloning animals" }, { id: "b", text: "Gene editing" }, { id: "c", text: "DNA fingerprinting" }, { id: "d", text: "Stem cell therapy" }] },
        { id: "q5", number: 5, text: "Montreal Protocol is related to:", options: [{ id: "a", text: "Ozone depletion" }, { id: "b", text: "Climate change" }, { id: "c", text: "Biodiversity" }, { id: "d", text: "Desertification" }] },
        { id: "q6", number: 6, text: "Which is NOT a quantitative tool of RBI?", options: [{ id: "a", text: "Bank Rate" }, { id: "b", text: "OMO" }, { id: "c", text: "SLR" }, { id: "d", text: "Margin Requirements" }] },
        { id: "q7", number: 7, text: "Ilmenite and rutile are sources of:", options: [{ id: "a", text: "Zinc" }, { id: "b", text: "Titanium" }, { id: "c", text: "Copper" }, { id: "d", text: "Lead" }] },
        { id: "q8", number: 8, text: "Project Tiger was launched in:", options: [{ id: "a", text: "1972" }, { id: "b", text: "1973" }, { id: "c", text: "1983" }, { id: "d", text: "1991" }] },
        { id: "q9", number: 9, text: "FEMA replaced FERA in:", options: [{ id: "a", text: "1997" }, { id: "b", text: "1999" }, { id: "c", text: "2001" }, { id: "d", text: "2003" }] },
        { id: "q10", number: 10, text: "Which organism makes tools to scrape insects?", options: [{ id: "a", text: "Chimpanzee" }, { id: "b", text: "Orangutan" }, { id: "c", text: "Eagle" }, { id: "d", text: "Crow" }] },
      ],
    },
  });
}

export async function POST() {
  return NextResponse.json({ success: true });
}
