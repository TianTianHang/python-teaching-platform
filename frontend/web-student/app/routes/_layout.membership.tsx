import { Box, Button, Card, CardActions, CardContent, CircularProgress, Container, Grid, Typography } from "@mui/material";
import createHttp from "~/utils/http/index.server";
import { withAuth } from "~/utils/loaderWrapper";
import type { Route } from "./+types/_layout.membership";
import type { MembershipType } from "~/types/user";
import type { Page } from "~/types/page";
import { Stars } from "@mui/icons-material";
import { useState } from "react";
import CheckoutModal from "~/components/CheckoutModal";
import { DEFAULT_META } from "~/config/meta";

/**
 * Route headers for HTTP caching
 * Membership page has static pricing content that can be cached publicly
 */
export function headers(): Headers | HeadersInit {
    return {
        "Cache-Control": "public, max-age=3600, s-maxage=3600, stale-while-revalidate=86400",
    };
}




export function HydrateFallback() {
    return <Container sx={{ py: 6, textAlign: 'center' }}>
        <CircularProgress />
        <Typography variant="body2" sx={{ mt: 2 }}>加载会员方案中...</Typography>
    </Container>
}
export const loader = withAuth(async ({ request }: Route.LoaderArgs) => {
    const http = createHttp(request);
    const membershipTypes = await http.get<Page<MembershipType>>("/membership-types/")
    return membershipTypes.results;
});
export default function MembershipPage({ loaderData }: Route.ComponentProps) {
    const membershipTypes = loaderData;
    const [open, setOpen] = useState(false);
    const [selected, setSelected] = useState<MembershipType>(membershipTypes[0])
    const handlePurchase = (id: number) => {
        setOpen(true)
        const find = membershipTypes.find(m => m.id == id);
        if (find) {
            setSelected(find)
        }

    }
    return (
        <>
          <title>会员方案 - {DEFAULT_META.siteName}</title>
          <Container sx={{ py: 6 }}>
            {/* <Typography variant="h4" align="center" gutterBottom>
        选择您的会员方案
      </Typography>
      <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 4 }}>
        开通会员，享受更多专属权益
      </Typography> */}

            <Grid container spacing={4} justifyContent="center">
                {membershipTypes.map((mt) => (
                    <Grid key={mt.id} size={{ xs: 12, sm: 6, md: 4 }}>
                        <Card
                            variant="outlined"
                            sx={{
                                height: '100%',
                                display: 'flex',
                                flexDirection: 'column',
                                borderRadius: 2,
                                boxShadow: 2,
                                '&:hover': {
                                    boxShadow: 4,
                                },
                            }}
                        >
                            <CardContent sx={{ flexGrow: 1 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                                    <Stars color="primary" sx={{ fontSize: 40 }} />
                                </Box>
                                <Typography variant="h6" align="center" gutterBottom>
                                    {mt.name}
                                </Typography>
                                <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 2 }}>
                                    {mt.description || `${mt.duration_days}天有效`}
                                </Typography>
                                <Typography variant="h5" align="center" color="primary" fontWeight="bold">
                                    ¥{mt.price}
                                </Typography>
                            </CardContent>
                            <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                                <Button
                                    variant="contained"
                                    color="primary"
                                    size="large"
                                    fullWidth
                                    onClick={() => handlePurchase(mt.id)}
                                    sx={{ maxWidth: 200 }}
                                >
                                    立即购买
                                </Button>
                            </CardActions>
                        </Card>
                    </Grid>
                ))}
            </Grid>
            <CheckoutModal open={open} onClose={() => setOpen(false)} membershipType={selected} />
        </Container>
        </>

    );

}
