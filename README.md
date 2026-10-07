# UPSC Test Analysis - React Frontend

A comprehensive React frontend for UPSC Prelims test analysis with Next.js 14+ (App Router).

## 📁 Structure

```
src/
├── app/
│   ├── layout.tsx          # Root layout with metadata
│   ├── globals.css         # Tailwind CSS v4 + design tokens
│   ├── providers.tsx       # Client providers
│   ├── page.tsx            # Dashboard (/)
│   ├── tests/[id]/
│   │   └── page.tsx        # Test taking page
│   └── tests/[id]/results/
│       └── page.tsx        # Results with mistake analysis
│   └── profile/
│       └── page.tsx        # Student profile with trends
└── components/
    ├── Navigation.tsx      # Sticky top navigation
    ├── ScoreCard.tsx       # Reusable stat display card
    ├── Timer.tsx           # Countdown timer with warnings
    ├── QuestionCard.tsx    # MCQ with options, review marking
    ├── QuestionPalette.tsx # Question navigator grid
    ├── MistakeCard.tsx     # Wrong answer analysis card
    ├── SubjectPieChart.tsx # Donut chart for subjects
    ├── RecommendationList.tsx # Personalized suggestions
    ├── FocusArea.tsx       # Topic accuracy with trend
    └── TestItem.tsx         # Test summary card
```

## 🎨 Design Tokens

- Brand Blue: `#1e40af`
- Wrong Red: `#dc143c`
- Correct Green: `#228b22`
- Warning Gold: `#b58934`

## 🔌 API Routes (Relative)

- `/api/dashboard` - Dashboard overview data
- `/api/tests/[id]` - Test details and questions
- `/api/tests/[id]/autosave` - POST auto-save answers
- `/api/tests/[id]/submit` - POST submit test
- `/api/tests/[id]/results` - Detailed results
- `/api/tests/[id]/results/pdf` - Download PDF report
- `/api/profile` - Student profile data

## 🚀 Features

- **Dashboard**: Subject-wise performance, focus areas, recent tests
- **Test Taking**: Timer, question palette, auto-save, review marking
- **Results**: Mistake analysis, recommendations, PDF download
- **Profile**: Improvement trends, strong/weak areas, activity log

## 📱 Accessibility

- ARIA labels and roles throughout
- Focus-visible styles for keyboard navigation
- Responsive design (mobile-first)
- Screen reader friendly