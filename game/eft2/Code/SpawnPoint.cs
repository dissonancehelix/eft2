public sealed class SpawnPoint : Component
{
	[Property] public TeamId Team { get; set; } = TeamId.none;
	[Property] public int Index { get; set; }
}
